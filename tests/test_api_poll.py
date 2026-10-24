from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Submission
from app.models.step import StepType
from tests.factories import make_answer, make_indicator, make_project, make_question, make_step


async def test_unknown_project_returns_404(client: AsyncClient) -> None:
    response = await client.get("/v1/does-not-exist/poll/steps")

    assert response.status_code == 404


async def test_full_poll_flow_returns_the_expected_envelope(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)
    question = await make_question(db_session, project, step)
    answer = await make_answer(db_session, project, question, weight=3)

    steps_response = await client.get(f"/v1/{project.code}/poll/steps", headers={"locale": "ru"})
    assert steps_response.status_code == 200
    assert steps_response.json()["status"] == "OK"
    assert len(steps_response.json()["data"]) == 1

    # exact request shape calc-web's http/api.ts sends: nested `region`, camelCase keys
    summary_response = await client.post(
        f"/v1/{project.code}/poll/summary",
        headers={"locale": "ru"},
        json={
            "region": {"regionId": 1, "areaId": -1},
            "answers": [
                {"stepId": step.id, "questionId": question.id, "answerId": answer.id}
            ],
        },
    )

    assert summary_response.status_code == 200
    body = summary_response.json()
    assert body["status"] == "OK"
    assert body["data"]["indicators"][0]["value"] == 3.0


async def test_responses_use_camel_case_field_names(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """calc-web's TypeScript types (IStep.nextStepId, IQuestion.stepId, ...) were
    written against the legacy Kotlin API, which serialized camelCase by default.
    A snake_case regression here breaks calc-web silently (fields read as
    undefined) rather than with an error."""
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step, high_risk_max=1, medium_risk_max=2)
    question = await make_question(db_session, project, step)
    await make_answer(db_session, project, question, weight=0)

    steps = (await client.get(f"/v1/{project.code}/poll/steps")).json()["data"]
    assert "nextStepId" in steps[0]
    assert "next_step_id" not in steps[0]

    questions = (await client.get(f"/v1/{project.code}/poll/assessment")).json()["data"]
    assert "stepId" in questions[0]
    assert "isMultiSelect" in questions[0]

    summary = (
        await client.post(f"/v1/{project.code}/poll/summary", json={"answers": []})
    ).json()
    assert "riskZone" in summary["data"]["indicators"][0]
    assert "riskText" in summary["data"]["indicators"][0]


async def test_locale_defaults_when_header_is_missing(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    await make_step(db_session, project)

    response = await client.get(f"/v1/{project.code}/poll/steps")

    assert response.status_code == 200
    assert response.json()["data"][0]["name"] == "Шаг"


async def test_secondary_locale_header_adds_the_mirror_fields(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    question = await make_question(
        db_session, project, step, content={"ru": "Вопрос", "ky": "Суроо"}
    )
    await make_answer(db_session, project, question, weight=3)

    response = await client.get(
        f"/v1/{project.code}/poll/assessment",
        headers={"locale": "ru", "secondary-locale": "ky"},
    )

    question_json = response.json()["data"][0]
    assert question_json["content"] == "Вопрос"
    assert question_json["contentSecondary"] == "Суроо"


async def test_response_carries_no_mirror_without_the_header(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """calc-web doesn't ask for a mirror and must keep seeing one language."""
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    question = await make_question(
        db_session, project, step, content={"ru": "Вопрос", "ky": "Суроо"}
    )
    await make_answer(db_session, project, question, weight=3)

    response = await client.get(
        f"/v1/{project.code}/poll/assessment", headers={"locale": "ru"}
    )

    assert response.json()["data"][0]["contentSecondary"] is None


async def test_summary_refuses_answers_the_project_does_not_have(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # a page loaded before a re-seed keeps posting ids that no longer exist;
    # scoring them would silently report zeros
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)
    question = await make_question(db_session, project, step)
    answer = await make_answer(db_session, project, question, weight=3)

    response = await client.post(
        f"/v1/{project.code}/poll/summary",
        json={
            "answers": [
                {"stepId": step.id, "questionId": question.id, "answerId": answer.id},
                {"stepId": step.id, "questionId": question.id, "answerId": answer.id + 10_000},
            ]
        },
    )

    assert response.status_code == 409


async def test_summary_refuses_another_projects_answers(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)
    other = await make_project(db_session)
    other_step = await make_step(db_session, other, type_=StepType.ASSESSMENT)
    other_question = await make_question(db_session, other, other_step)
    other_answer = await make_answer(db_session, other, other_question, weight=3)

    response = await client.post(
        f"/v1/{project.code}/poll/summary",
        json={
            "answers": [
                {
                    "stepId": other_step.id,
                    "questionId": other_question.id,
                    "answerId": other_answer.id,
                }
            ]
        },
    )

    assert response.status_code == 409


async def test_summary_is_stored_for_statistics(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)
    question = await make_question(db_session, project, step)
    answer = await make_answer(db_session, project, question, weight=2)
    # the endpoint commits, which expires these objects
    project_id, step_code, question_code = project.id, step.code, question.code
    answer_id, answer_code = answer.id, answer.code

    response = await client.post(
        f"/v1/{project.code}/poll/summary",
        headers={"locale": "ky", "secondary-locale": "ru", "user-agent": "test-agent"},
        json={
            "answers": [{"stepId": step.id, "questionId": question.id, "answerId": answer_id}],
            "sessionId": "session-1",
            "deviceId": "device-1",
            "source": "radar",
        },
    )
    assert response.status_code == 200

    stored = (
        await db_session.scalars(select(Submission).where(Submission.project_id == project_id))
    ).all()
    assert len(stored) == 1
    record = stored[0]
    assert (record.session_id, record.source, record.locale, record.secondary_locale) == (
        "session-1",
        "radar",
        "ky",
        "ru",
    )
    assert record.device_id == "device-1"
    assert record.is_complete is True
    assert record.user_agent == "test-agent"
    assert record.answers == [
        {
            "step_code": step_code,
            "question_code": question_code,
            "answer_code": answer_code,
            "answer_id": answer_id,
            "weight": 2,
        }
    ]
    assert record.indicators[0]["value"] == 2.0


async def test_refused_summary_is_not_stored(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)

    response = await client.post(
        f"/v1/{project.code}/poll/summary",
        json={"answers": [{"stepId": step.id, "questionId": 1, "answerId": 999_999_999}]},
    )
    assert response.status_code == 409

    stored = (
        await db_session.scalars(select(Submission).where(Submission.project_id == project.id))
    ).all()
    assert stored == []
