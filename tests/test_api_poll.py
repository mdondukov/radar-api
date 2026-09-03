from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
