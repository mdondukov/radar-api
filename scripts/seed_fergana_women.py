"""Seed: load the "Женщины Ферганы" project from scripts/data/fergana_women.json
into the radar-api schema.

Unlike scripts/etl_zhashyl_climate.py, there is no legacy source database here —
the questionnaire only ever existed as a PDF/docx, manually transcribed into the
JSON file (see docs/fergana-women-content-spec.md for the mapping decisions).

The seed updates the project in place, matching rows by their codes
(fergana-indicator-N, indicator-N, question-N-M, answer-N-M-K): existing rows keep
their ids, new ones are inserted, rows no longer in the JSON are deleted. Ids
must stay stable because a page loaded before a re-seed keeps posting the ids it
fetched; replacing the project wholesale gave every row a new id and silently
zeroed the radar of everyone mid-questionnaire (22 October 2026).

The REGION step and the Region/Area tree belong to copy_regions_to_fergana.py and
are left alone, except that the REGION step is kept at the head of the chain.

Usage:
    PYTHONPATH=. uv run python scripts/seed_fergana_women.py
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models import Answer, Indicator, Project, Question, Step
from app.models.step import StepType

DATA_PATH = Path(__file__).parent / "data" / "fergana_women.json"

RADAR_STEP_CODE = "fergana-radar"


def loc(value: dict[str, str] | None) -> dict[str, str] | None:
    """The JSON already stores localized text as {"ru": ..., "ky": ...} (or null) —
    this just documents the shape passed through to each model field."""
    return value


def assign(row: Any, **fields: Any) -> None:
    for name, value in fields.items():
        setattr(row, name, value)


async def upsert_project(db: AsyncSession, code: str, name: str) -> Project:
    project = await db.scalar(select(Project).where(Project.code == code))
    if project is None:
        project = Project(code=code, name=name, default_locale="ru")
        db.add(project)
    else:
        project.name = name
    await db.flush()
    return project


async def upsert_step(
    db: AsyncSession, project: Project, existing: dict[str, Step], code: str, **fields: Any
) -> Step:
    step = existing.get(code)
    if step is None:
        step = Step(project_id=project.id, code=code, next_step_id=None, **fields)
        db.add(step)
    else:
        assign(step, **fields)
    await db.flush()
    return step


async def load_answers(
    db: AsyncSession, project: Project, question: Question, prefix: str, answers: list[Any]
) -> None:
    existing = {
        a.code: a
        for a in (await db.scalars(select(Answer).where(Answer.question_id == question.id))).all()
    }
    wanted = set()
    for a_ord, a_data in enumerate(answers, start=1):
        code = f"{prefix}-{a_ord}"
        wanted.add(code)
        fields = dict(
            content=loc(a_data["content"]),
            descr=loc(a_data.get("descr")),
            weight=a_data["weight"],
            recommendation=loc(a_data.get("recommendation")),
            ord=a_ord,
        )
        answer = existing.get(code)
        if answer is None:
            db.add(Answer(project_id=project.id, question_id=question.id, code=code, **fields))
        else:
            assign(answer, **fields)
    for code, answer in existing.items():
        if code not in wanted:
            await db.delete(answer)


async def load_indicator(
    db: AsyncSession,
    project: Project,
    steps: dict[str, Step],
    ind_data: dict[str, Any],
    step_ord: int,
) -> Step:
    ord_ = ind_data["ord"]
    step = await upsert_step(
        db,
        project,
        steps,
        f"fergana-indicator-{ord_}",
        name=loc(ind_data["name"]),
        intro=loc(ind_data.get("intro")),
        descr=loc(ind_data.get("descr")),
        type=StepType.ASSESSMENT,
        ord=step_ord,
    )

    code = f"indicator-{ord_}"
    fields = dict(
        step_id=step.id,
        name=loc(ind_data["name"]),
        ord=ord_,
        high_risk_max=ind_data["high_risk_max"],
        medium_risk_max=ind_data["medium_risk_max"],
        high_risk_text=loc(ind_data.get("high_risk_text")),
        medium_risk_text=loc(ind_data.get("medium_risk_text")),
        low_risk_text=loc(ind_data.get("low_risk_text")),
    )
    indicator = await db.scalar(
        select(Indicator).where(Indicator.project_id == project.id, Indicator.code == code)
    )
    if indicator is None:
        db.add(Indicator(project_id=project.id, code=code, **fields))
    else:
        assign(indicator, **fields)

    questions = {
        q.code: q
        for q in (await db.scalars(select(Question).where(Question.step_id == step.id))).all()
    }
    wanted = set()
    for q_data in ind_data["questions"]:
        q_ord = q_data["ord"]
        q_code = f"question-{ord_}-{q_ord}"
        wanted.add(q_code)
        fields = dict(
            content=loc(q_data["content"]),
            descr=loc(q_data.get("descr")),
            is_multi_select=q_data.get("is_multi_select", False),
            ord=q_ord,
        )
        question = questions.get(q_code)
        if question is None:
            question = Question(project_id=project.id, step_id=step.id, code=q_code, **fields)
            db.add(question)
            await db.flush()
        else:
            assign(question, **fields)
        await load_answers(db, project, question, f"answer-{ord_}-{q_ord}", q_data["answers"])
    for q_code, question in questions.items():
        if q_code not in wanted:
            await db.delete(question)

    await db.flush()
    return step


async def seed(db: AsyncSession, data: dict[str, Any]) -> Project:
    project = await upsert_project(db, data["project"]["code"], data["project"]["name"])
    steps = {
        s.code: s
        for s in (await db.scalars(select(Step).where(Step.project_id == project.id))).all()
    }
    region_step = next((s for s in steps.values() if s.type == StepType.REGION), None)
    offset = 1 if region_step is not None else 0

    chain: list[Step] = [region_step] if region_step is not None else []
    for ind_data in data["indicators"]:
        chain.append(await load_indicator(db, project, steps, ind_data, ind_data["ord"] + offset))
    chain.append(
        await upsert_step(
            db,
            project,
            steps,
            RADAR_STEP_CODE,
            name=loc(data["radar_step"]["name"]),
            intro=None,
            descr=None,
            type=StepType.RADAR,
            ord=len(data["indicators"]) + 1 + offset,
        )
    )

    # Self-referential FK: every step exists by now, so the chain can be relinked.
    for current, next_ in zip(chain, chain[1:] + [None], strict=True):
        current.next_step_id = next_.id if next_ is not None else None
    await db.flush()

    kept = {s.id for s in chain}
    for step in steps.values():
        if step.id not in kept:
            await db.delete(step)
    await db.flush()
    return project


async def count(db: AsyncSession, model: Any, project: Project) -> int:
    query = select(func.count()).select_from(model).where(model.project_id == project.id)
    return (await db.scalar(query)) or 0


async def main() -> None:
    data = json.loads(DATA_PATH.read_text())

    async with SessionLocal() as db:
        project = await seed(db, data)
        await db.commit()

    async with SessionLocal() as db:
        counts = {
            "step": await count(db, Step, project),
            "indicator": await count(db, Indicator, project),
            "question": await count(db, Question, project),
            "answer": await count(db, Answer, project),
        }
        print(f"seeded project code={data['project']['code']!r}: {counts}")


if __name__ == "__main__":
    asyncio.run(main())
