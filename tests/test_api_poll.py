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

    summary_response = await client.post(
        f"/v1/{project.code}/poll/summary",
        headers={"locale": "ru"},
        json={
            "answers": [
                {"step_id": step.id, "question_id": question.id, "answer_id": answer.id}
            ]
        },
    )

    assert summary_response.status_code == 200
    body = summary_response.json()
    assert body["status"] == "OK"
    assert body["data"]["indicators"][0]["value"] == 3.0


async def test_locale_defaults_when_header_is_missing(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    await make_step(db_session, project)

    response = await client.get(f"/v1/{project.code}/poll/steps")

    assert response.status_code == 200
    assert response.json()["data"][0]["name"] == "Шаг"
