"""One-off: copy the Region/Area tree from zhashyl-climate into fergana-women,
and insert a REGION step at the front of its step chain.

fergana-women intentionally reuses the exact same regions as zhashyl-climate (same
physical breakdown of Kyrgyzstan, not a Fergana-specific one) — confirmed by the
user. Region/Area rows are project-scoped (via project_id), so they cannot be
literally shared between two projects; this copies the rows verbatim (same
code/name/descr/impact/ord) under their own primary keys instead. Re-runs update
the rows in place, matched by code, so those keys stay stable.

Usage:
    PYTHONPATH=. uv run python scripts/copy_regions_to_fergana.py
"""

import asyncio

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models import Area, Project, Region, Step
from app.models.step import StepType

SOURCE_PROJECT_CODE = "zhashyl-climate"
TARGET_PROJECT_CODE = "fergana-women"


async def get_project(db: AsyncSession, code: str) -> Project:
    project = await db.scalar(select(Project).where(Project.code == code))
    if project is None:
        raise RuntimeError(f"project not found: {code!r}")
    return project


async def copy_regions(db: AsyncSession, source: Project, target: Project) -> None:
    """Upsert by code, so re-runs keep the target's Region/Area ids stable (see the
    note on stable ids in seed_fergana_women.py)."""
    source_regions = (
        await db.scalars(select(Region).where(Region.project_id == source.id).order_by(Region.ord))
    ).all()
    source_areas = (
        await db.scalars(select(Area).where(Area.project_id == source.id).order_by(Area.ord))
    ).all()
    target_regions = {
        r.code: r
        for r in (await db.scalars(select(Region).where(Region.project_id == target.id))).all()
    }

    areas_by_region_id: dict[int, list[Area]] = {}
    for area in source_areas:
        areas_by_region_id.setdefault(area.region_id, []).append(area)

    for region in source_regions:
        target_region = target_regions.pop(region.code, None)
        if target_region is None:
            target_region = Region(project_id=target.id, code=region.code)
            db.add(target_region)
        target_region.name = region.name
        target_region.descr = region.descr
        target_region.ord = region.ord
        await db.flush()

        target_areas = {
            a.code: a
            for a in (
                await db.scalars(select(Area).where(Area.region_id == target_region.id))
            ).all()
        }
        for area in areas_by_region_id.get(region.id, []):
            target_area = target_areas.pop(area.code, None)
            if target_area is None:
                target_area = Area(project_id=target.id, region_id=target_region.id, code=area.code)
                db.add(target_area)
            target_area.name = area.name
            target_area.descr = area.descr
            target_area.impact = area.impact
            target_area.ord = area.ord
        for stale in target_areas.values():
            await db.delete(stale)

    for stale_region in target_regions.values():
        await db.delete(stale_region)
    await db.flush()


async def insert_region_step(db: AsyncSession, source: Project, target: Project) -> None:
    existing = await db.scalar(
        select(Step).where(Step.project_id == target.id, Step.type == StepType.REGION)
    )
    if existing is not None:
        return

    source_region_step = await db.scalar(
        select(Step).where(Step.project_id == source.id, Step.type == StepType.REGION)
    )
    if source_region_step is None:
        raise RuntimeError(f"no REGION step found on source project {source.code!r}")

    other_steps = (
        await db.scalars(select(Step).where(Step.project_id == target.id).order_by(Step.ord))
    ).all()
    for step in other_steps:
        await db.execute(update(Step).where(Step.id == step.id).values(ord=step.ord + 1))
    await db.flush()

    region_step = Step(
        project_id=target.id,
        code="fergana-region",
        name=source_region_step.name,
        intro=source_region_step.intro,
        descr=source_region_step.descr,
        type=StepType.REGION,
        next_step_id=other_steps[0].id if other_steps else None,
        ord=1,
    )
    db.add(region_step)
    await db.flush()


async def main() -> None:
    async with SessionLocal() as db:
        source = await get_project(db, SOURCE_PROJECT_CODE)
        target = await get_project(db, TARGET_PROJECT_CODE)

        await copy_regions(db, source, target)
        await insert_region_step(db, source, target)

        await db.commit()

    async with SessionLocal() as db:
        target = await get_project(db, TARGET_PROJECT_CODE)
        counts = {
            "region": len(
                (await db.scalars(select(Region.id).where(Region.project_id == target.id))).all()
            ),
            "area": len(
                (await db.scalars(select(Area.id).where(Area.project_id == target.id))).all()
            ),
            "step": len(
                (await db.scalars(select(Step.id).where(Step.project_id == target.id))).all()
            ),
        }
        print(f"copied regions into project code={TARGET_PROJECT_CODE!r}: {counts}")


if __name__ == "__main__":
    asyncio.run(main())
