"""One-off seed: load the "Женщины Ферганы" project from
scripts/data/fergana_women.json into the radar-api schema.

Unlike scripts/etl_zhashyl_climate.py, there is no legacy source database here —
the questionnaire only ever existed as a PDF/docx, manually transcribed into the
JSON file (see docs/fergana-women-content-spec.md for the mapping decisions).

Usage:
    PYTHONPATH=. uv run python scripts/seed_fergana_women.py
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models import Answer, Indicator, Project, Question, Step
from app.models.step import StepType

DATA_PATH = Path(__file__).parent / "data" / "fergana_women.json"


def loc(value: dict[str, str] | None) -> dict[str, str] | None:
    """The JSON already stores localized text as {"ru": ..., "ky": ...} (or null) —
    this just documents the shape passed through to each model field."""
    return value


async def replace_project(db: AsyncSession, code: str, name: str) -> Project:
    await db.execute(delete(Project).where(Project.code == code))
    project = Project(code=code, name=name, default_locale="ru")
    db.add(project)
    await db.flush()
    return project


async def load_indicator(
    db: AsyncSession, project: Project, ind_data: dict[str, Any]
) -> int:
    ord_ = ind_data["ord"]
    step_code = f"fergana-indicator-{ord_}"

    step = Step(
        project_id=project.id,
        code=step_code,
        name=loc(ind_data["name"]),
        intro=loc(ind_data.get("intro")),
        descr=loc(ind_data.get("descr")),
        type=StepType.ASSESSMENT,
        next_step_id=None,
        ord=ord_,
    )
    db.add(step)
    await db.flush()

    indicator = Indicator(
        project_id=project.id,
        step_id=step.id,
        code=f"indicator-{ord_}",
        name=loc(ind_data["name"]),
        ord=ord_,
        high_risk_max=ind_data["high_risk_max"],
        medium_risk_max=ind_data["medium_risk_max"],
        high_risk_text=loc(ind_data.get("high_risk_text")),
        medium_risk_text=loc(ind_data.get("medium_risk_text")),
        low_risk_text=loc(ind_data.get("low_risk_text")),
    )
    db.add(indicator)
    await db.flush()

    for q_data in ind_data["questions"]:
        q_ord = q_data["ord"]
        question = Question(
            project_id=project.id,
            step_id=step.id,
            code=f"question-{ord_}-{q_ord}",
            content=loc(q_data["content"]),
            descr=loc(q_data.get("descr")),
            is_multi_select=q_data.get("is_multi_select", False),
            ord=q_ord,
        )
        db.add(question)
        await db.flush()

        for a_ord, a_data in enumerate(q_data["answers"], start=1):
            db.add(
                Answer(
                    project_id=project.id,
                    question_id=question.id,
                    code=f"answer-{ord_}-{q_ord}-{a_ord}",
                    content=loc(a_data["content"]),
                    descr=loc(a_data.get("descr")),
                    weight=a_data["weight"],
                    recommendation=loc(a_data.get("recommendation")),
                    ord=a_ord,
                )
            )
    await db.flush()
    return step.id


async def load_radar_step(
    db: AsyncSession, project: Project, radar_data: dict[str, Any], ord_: int
) -> int:
    step = Step(
        project_id=project.id,
        code="fergana-radar",
        name=loc(radar_data["name"]),
        intro=None,
        descr=None,
        type=StepType.RADAR,
        next_step_id=None,
        ord=ord_,
    )
    db.add(step)
    await db.flush()
    return step.id


async def link_steps_in_order(db: AsyncSession, step_ids_in_order: list[int]) -> None:
    """Self-referential FK: every step must already exist before any next_step_id
    can point to it, so this always runs as a second pass after all steps are created."""
    for current_id, next_id in zip(step_ids_in_order, step_ids_in_order[1:], strict=False):
        await db.execute(update(Step).where(Step.id == current_id).values(next_step_id=next_id))
    await db.flush()


async def main() -> None:
    data = json.loads(DATA_PATH.read_text())

    async with SessionLocal() as db:
        project = await replace_project(
            db, data["project"]["code"], data["project"]["name"]
        )

        step_ids_in_order = []
        for ind_data in data["indicators"]:
            step_ids_in_order.append(await load_indicator(db, project, ind_data))

        step_ids_in_order.append(
            await load_radar_step(
                db, project, data["radar_step"], ord_=len(data["indicators"]) + 1
            )
        )

        await link_steps_in_order(db, step_ids_in_order)

        await db.commit()

    async with SessionLocal() as db:
        counts = {
            "step": len(
                (
                    await db.scalars(
                        select(Step.id).where(Step.project_id == project.id)
                    )
                ).all()
            ),
            "indicator": len(
                (
                    await db.scalars(
                        select(Indicator.id).where(Indicator.project_id == project.id)
                    )
                ).all()
            ),
            "question": len(
                (
                    await db.scalars(
                        select(Question.id).where(Question.project_id == project.id)
                    )
                ).all()
            ),
            "answer": len(
                (
                    await db.scalars(
                        select(Answer.id).where(Answer.project_id == project.id)
                    )
                ).all()
            ),
        }
        print(f"seeded project code={data['project']['code']!r}: {counts}")


if __name__ == "__main__":
    asyncio.run(main())
