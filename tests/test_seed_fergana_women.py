import copy
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Indicator, Question, Step
from app.models.step import StepType
from scripts.seed_fergana_women import seed


def _data(code: str) -> dict[str, Any]:
    def indicator(ord_: int) -> dict[str, Any]:
        return {
            "ord": ord_,
            "name": {"ru": f"Показатель {ord_}"},
            "intro": None,
            "descr": {"ru": "описание"},
            "high_risk_max": 1.0,
            "medium_risk_max": 2.0,
            "high_risk_text": {"ru": "высокий"},
            "medium_risk_text": None,
            "low_risk_text": None,
            "questions": [
                {
                    "ord": q,
                    "content": {"ru": f"Вопрос {q}"},
                    "answers": [
                        {
                            "content": {"ru": "нет"},
                            "weight": 0,
                            "recommendation": {"ru": "сделать"},
                        },
                        {"content": {"ru": "да"}, "weight": 3},
                    ],
                }
                for q in (1, 2)
            ],
        }

    return {
        "project": {"code": code, "name": "Test"},
        "indicators": [indicator(1), indicator(2)],
        "radar_step": {"name": {"ru": "Радар"}},
    }


async def _ids(db: AsyncSession, project_id: int) -> dict[str, dict[str, int]]:
    models: tuple[Any, ...] = (Step, Indicator, Question, Answer)
    return {
        model.__name__: {
            row.code: row.id
            for row in (await db.scalars(select(model).where(model.project_id == project_id)))
        }
        for model in models
    }


async def test_reseed_keeps_ids_and_updates_texts(db_session: AsyncSession) -> None:
    data = _data("seed-test-stable")
    project = await seed(db_session, data)
    before = await _ids(db_session, project.id)

    changed = copy.deepcopy(data)
    changed["indicators"][0]["questions"][0]["content"] = {"ru": "Новый вопрос", "ky": "Жаңы"}
    changed["indicators"][0]["questions"][0]["answers"][0]["recommendation"] = {"ru": "иначе"}
    await seed(db_session, changed)

    assert await _ids(db_session, project.id) == before
    question = await db_session.scalar(select(Question).where(Question.code == "question-1-1"))
    assert question is not None and question.content == {"ru": "Новый вопрос", "ky": "Жаңы"}


async def test_reseed_removes_rows_dropped_from_the_json(db_session: AsyncSession) -> None:
    data = _data("seed-test-removal")
    project = await seed(db_session, data)

    trimmed = copy.deepcopy(data)
    trimmed["indicators"][1]["questions"].pop()
    trimmed["indicators"][0]["questions"][0]["answers"].pop()
    await seed(db_session, trimmed)

    ids = await _ids(db_session, project.id)
    assert "question-2-2" not in ids["Question"]
    assert "answer-2-2-1" not in ids["Answer"]
    assert "answer-1-1-2" not in ids["Answer"]
    assert "answer-1-1-1" in ids["Answer"]


async def test_reseed_keeps_the_region_step_at_the_head(db_session: AsyncSession) -> None:
    data = _data("seed-test-region")
    project = await seed(db_session, data)
    first = await db_session.scalar(
        select(Step).where(Step.project_id == project.id, Step.code == "fergana-indicator-1")
    )
    assert first is not None
    region = Step(
        project_id=project.id,
        code="fergana-region",
        name={"ru": "Регион"},
        type=StepType.REGION,
        next_step_id=first.id,
        ord=1,
    )
    db_session.add(region)
    await db_session.flush()

    await seed(db_session, data)

    steps = (
        await db_session.scalars(
            select(Step).where(Step.project_id == project.id).order_by(Step.ord)
        )
    ).all()
    assert [s.code for s in steps] == [
        "fergana-region",
        "fergana-indicator-1",
        "fergana-indicator-2",
        "fergana-radar",
    ]
    assert [s.ord for s in steps] == [1, 2, 3, 4]
    assert [s.next_step_id for s in steps] == [steps[1].id, steps[2].id, steps[3].id, None]
