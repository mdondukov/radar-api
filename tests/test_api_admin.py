import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.step import StepType
from app.services import admin_auth
from tests.factories import make_answer, make_indicator, make_project, make_question, make_step

ADMIN = "admin@example.org"


@pytest.fixture
def admin_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "google_client_id", "client-id")
    monkeypatch.setattr(settings, "admin_session_secret", "x" * 32)
    monkeypatch.setattr(settings, "admin_emails", [ADMIN])
    # the test client talks plain http, where a Secure cookie is not sent back
    monkeypatch.setattr(settings, "admin_cookie_secure", False)

    def fake_verify(credential: str) -> str:
        # stands in for the Google signature check: the "token" is the email
        if credential != ADMIN:
            raise admin_auth.AdminAuthError("not allowed")
        return credential

    monkeypatch.setattr(admin_auth, "_verify_google_token", fake_verify)


async def test_admin_is_off_until_configured(client: AsyncClient) -> None:
    response = await client.post("/v1/admin/session", json={"credential": "x"})

    assert response.status_code == 503


@pytest.mark.usefixtures("admin_enabled")
async def test_sign_in_sets_a_session_cookie(client: AsyncClient) -> None:
    response = await client.post("/v1/admin/session", json={"credential": ADMIN})

    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "radar_admin=" in cookie
    assert "HttpOnly" in cookie and "Path=/admin" in cookie and "SameSite=strict" in cookie
    client.cookies.set("radar_admin", response.cookies["radar_admin"])
    me = await client.get("/v1/admin/session")
    assert me.json()["data"]["email"] == ADMIN


@pytest.mark.usefixtures("admin_enabled")
async def test_sign_in_refuses_anyone_else(client: AsyncClient) -> None:
    response = await client.post("/v1/admin/session", json={"credential": "x@example.org"})

    assert response.status_code == 403
    assert "set-cookie" not in response.headers


@pytest.mark.usefixtures("admin_enabled")
async def test_session_ends_when_the_email_leaves_the_allow_list(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    token = admin_auth.issue_session(ADMIN)
    monkeypatch.setattr(settings, "admin_emails", [])

    client.cookies.set("radar_admin", token)
    response = await client.get("/v1/admin/session")

    assert response.status_code == 401


@pytest.mark.usefixtures("admin_enabled")
async def test_stats_need_a_session(client: AsyncClient, db_session: AsyncSession) -> None:
    project = await make_project(db_session)

    response = await client.get(f"/v1/admin/{project.code}/stats")

    assert response.status_code == 401


@pytest.mark.usefixtures("admin_enabled")
async def test_stats_carry_the_questionnaire_submissions_and_log_history(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project, type_=StepType.ASSESSMENT)
    await make_indicator(db_session, project, step)
    question = await make_question(db_session, project, step)
    answer = await make_answer(db_session, project, question, weight=1)
    code, step_id, question_id, answer_id = project.code, step.id, question.id, answer.id
    await client.post(
        f"/v1/{code}/poll/summary",
        headers={"user-agent": "Mozilla/5.0 (iPhone)"},
        json={
            "answers": [{"stepId": step_id, "questionId": question_id, "answerId": answer_id}],
            "sessionId": "s1",
            "source": "radar",
        },
    )

    client.cookies.set("radar_admin", admin_auth.issue_session(ADMIN))
    response = await client.get(f"/v1/admin/{code}/stats")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["indicators"]) == 1
    assert len(data["indicators"][0]["questions"][0]["answers"]) == 1
    [submission] = data["submissions"]
    assert submission["session_id"] == "s1"
    assert submission["device"] == "mobile"
    assert len(data["log_history"]["sessions"]) > 0
