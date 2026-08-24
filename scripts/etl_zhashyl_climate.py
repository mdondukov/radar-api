"""One-off ETL: import the "Жашыл климат" project from the legacy Kotlin/Postgres
`calc` schema into the new radar-api schema.

Source is expected to be a *local, disposable copy* of the `calc` schema
(e.g. restored from a `pg_dump -n calc` of the production DB) — this script
never talks to production. It preserves source primary keys 1:1 across all
tables so foreign keys need no remapping, then resets target sequences.

Usage:
    PYTHONPATH=. uv run python scripts/etl_zhashyl_climate.py

Env:
    SOURCE_DATABASE_URL   postgres DSN for the copied `calc` schema
                           (default: local `calc_zhashyl_export` db)
"""

import asyncio
import os
from typing import Any

import asyncpg
from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models import Answer, Area, Indicator, Project, Question, Region, Step
from app.models.step import StepType

SOURCE_DSN = os.environ.get(
    "SOURCE_DATABASE_URL", "postgresql://radar:radar@localhost:5433/calc_zhashyl_export"
)
PROJECT_CODE = "zhashyl-climate"
PROJECT_NAME = "Жашыл климат"

TABLES_WITH_PRESERVED_IDS = ["step", "region", "area", "indicator", "question", "answer"]


def merge_translations(
    base_ru: str | None, translations: dict[str, str] | None
) -> dict[str, str] | None:
    result: dict[str, str] = {}
    if base_ru:
        result["ru"] = base_ru
    if translations:
        for locale, text_ in translations.items():
            if text_:
                result[locale] = text_
    return result or None


async def fetch_lang_map(
    conn: asyncpg.Connection, table: str, fk_column: str
) -> dict[int, dict[str, Any]]:
    rows = await conn.fetch(f"SELECT * FROM calc.{table}")
    return {row[fk_column]: dict(row) for row in rows}


async def load_source() -> dict[str, Any]:
    conn = await asyncpg.connect(SOURCE_DSN)
    await conn.set_builtin_type_codec("hstore", schema="public", codec_name="pg_contrib.hstore")
    try:
        steps = await conn.fetch("SELECT * FROM calc.step ORDER BY id")
        step_lang = await fetch_lang_map(conn, "step_lang", "step_id")
        next_rows = await conn.fetch("SELECT * FROM calc.step_cascade_next")
        next_map = {r["step_id"]: r["next_id"] for r in next_rows}

        regions = await conn.fetch("SELECT * FROM calc.region ORDER BY id")
        region_lang = await fetch_lang_map(conn, "region_lang", "region_id")

        areas = await conn.fetch("SELECT * FROM calc.area ORDER BY id")
        area_lang = await fetch_lang_map(conn, "area_lang", "area_id")

        indicators = await conn.fetch("SELECT * FROM calc.indicator ORDER BY id")
        indicator_lang = await fetch_lang_map(conn, "indicator_lang", "indicator_id")

        questions = await conn.fetch("SELECT * FROM calc.question ORDER BY id")
        question_lang = await fetch_lang_map(conn, "question_lang", "question_id")

        answers = await conn.fetch("SELECT * FROM calc.answer ORDER BY id")
        answer_lang = await fetch_lang_map(conn, "answer_lang", "answer_id")
    finally:
        await conn.close()

    return {
        "steps": steps,
        "step_lang": step_lang,
        "next_map": next_map,
        "regions": regions,
        "region_lang": region_lang,
        "areas": areas,
        "area_lang": area_lang,
        "indicators": indicators,
        "indicator_lang": indicator_lang,
        "questions": questions,
        "question_lang": question_lang,
        "answers": answers,
        "answer_lang": answer_lang,
    }


async def replace_project(db: AsyncSession) -> Project:
    await db.execute(delete(Project).where(Project.code == PROJECT_CODE))
    project = Project(code=PROJECT_CODE, name=PROJECT_NAME, default_locale="ru")
    db.add(project)
    await db.flush()
    return project


async def load_target(db: AsyncSession, project: Project, src: dict[str, Any]) -> None:
    # next_step_id is self-referential: inserted as NULL first, backfilled once every
    # step row exists, otherwise the FK to a not-yet-inserted step row would fail.
    for s in src["steps"]:
        lang = src["step_lang"].get(s["id"])
        db.add(
            Step(
                id=s["id"],
                project_id=project.id,
                code=f"step-{s['id']}",
                name=merge_translations(s["name"], lang and lang.get("name")),
                descr=merge_translations(s["descr"], lang and lang.get("descr")),
                type=StepType(s["type"]),
                next_step_id=None,
                is_active=s["active"],
                ord=s["ord"],
            )
        )
    await db.flush()

    for step_id, next_id in src["next_map"].items():
        await db.execute(update(Step).where(Step.id == step_id).values(next_step_id=next_id))
    await db.flush()

    for i, r in enumerate(src["regions"], start=1):
        lang = src["region_lang"].get(r["id"])
        db.add(
            Region(
                id=r["id"],
                project_id=project.id,
                code=f"region-{r['id']}",
                name=merge_translations(r["name"], lang and lang.get("name")),
                descr=merge_translations(r["descr"], lang and lang.get("descr")),
                ord=i,
            )
        )
    await db.flush()

    for a in src["areas"]:
        lang = src["area_lang"].get(a["id"])
        db.add(
            Area(
                id=a["id"],
                project_id=project.id,
                region_id=a["region_id"],
                code=f"area-{a['id']}",
                name=merge_translations(a["name"], lang and lang.get("name")),
                descr=merge_translations(a["descr"], lang and lang.get("descr")),
                impact=merge_translations(a["impact"], lang and lang.get("impact")),
                ord=a["ord"],
            )
        )
    await db.flush()

    for ind in src["indicators"]:
        lang = src["indicator_lang"].get(ind["id"])
        db.add(
            Indicator(
                id=ind["id"],
                project_id=project.id,
                step_id=ind["step_id"],
                code=f"indicator-{ind['id']}",
                name=merge_translations(ind["name"], lang and lang.get("name")),
                ord=ind["ord"],
            )
        )
    await db.flush()

    for q in src["questions"]:
        lang = src["question_lang"].get(q["id"])
        db.add(
            Question(
                id=q["id"],
                project_id=project.id,
                step_id=q["step_id"],
                code=f"question-{q['id']}",
                content=merge_translations(q["content"], lang and lang.get("content")),
                descr=merge_translations(q["descr"], lang and lang.get("descr")),
                is_active=q["active"],
                ord=q["ord"],
            )
        )
    await db.flush()

    for ans in src["answers"]:
        lang = src["answer_lang"].get(ans["id"])
        db.add(
            Answer(
                id=ans["id"],
                project_id=project.id,
                question_id=ans["question_id"],
                code=f"answer-{ans['id']}",
                content=merge_translations(ans["content"], lang and lang.get("content")),
                descr=merge_translations(ans["descr"], lang and lang.get("descr")),
                weight=ans["weight"],
                ord=ans["ord"],
            )
        )


async def reset_sequences(db: AsyncSession) -> None:
    for table in TABLES_WITH_PRESERVED_IDS:
        await db.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            )
        )


async def main() -> None:
    src = await load_source()
    async with SessionLocal() as db:
        project = await replace_project(db)
        await load_target(db, project, src)
        await db.flush()
        await reset_sequences(db)
        await db.commit()

    async with SessionLocal() as db:
        counts = {
            "step": len((await db.scalars(select(Step.id))).all()),
            "region": len((await db.scalars(select(Region.id))).all()),
            "area": len((await db.scalars(select(Area.id))).all()),
            "indicator": len((await db.scalars(select(Indicator.id))).all()),
            "question": len((await db.scalars(select(Question.id))).all()),
            "answer": len((await db.scalars(select(Answer.id))).all()),
        }
        print(f"imported project code={PROJECT_CODE!r}: {counts}")


if __name__ == "__main__":
    asyncio.run(main())
