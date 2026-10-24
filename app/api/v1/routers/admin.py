from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel

from app.api.deps import DbSession, ProjectDep
from app.core.config import settings
from app.schemas.common import ApiResponse
from app.services import admin_auth, admin_stats_service

router = APIRouter(prefix="/v1/admin", tags=["admin"])

# Served to the browser as /admin/api/... by nginx on the dashboard's own host,
# so the cookie is first-party and scoped to the dashboard.
COOKIE_PATH = "/admin"


class SignInIn(BaseModel):
    credential: str


class AdminOut(BaseModel):
    email: str


def _require_enabled() -> None:
    if not admin_auth.enabled():
        raise HTTPException(status_code=503, detail="Admin is not configured")


def current_admin(
    radar_admin: Annotated[str | None, Cookie()] = None,
) -> str:
    _require_enabled()
    email = admin_auth.read_session(radar_admin)
    if email is None:
        raise HTTPException(status_code=401, detail="Sign in required")
    return email


AdminDep = Annotated[str, Depends(current_admin)]


@router.post("/session")
async def sign_in(body: SignInIn, response: Response) -> ApiResponse[AdminOut]:
    _require_enabled()
    try:
        email = await admin_auth.sign_in(body.credential)
    except admin_auth.AdminAuthError as exc:
        # one answer for every failure: no hint whether the email is known
        raise HTTPException(status_code=403, detail="Access denied") from exc
    response.set_cookie(
        admin_auth.SESSION_COOKIE,
        admin_auth.issue_session(email),
        max_age=settings.admin_session_days * 24 * 3600,
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.admin_cookie_secure,
        samesite="strict",
    )
    return ApiResponse(data=AdminOut(email=email))


@router.get("/session")
async def session(email: AdminDep) -> ApiResponse[AdminOut]:
    return ApiResponse(data=AdminOut(email=email))


@router.delete("/session")
async def sign_out(response: Response) -> ApiResponse[None]:
    response.delete_cookie(admin_auth.SESSION_COOKIE, path=COOKIE_PATH)
    return ApiResponse(data=None)


@router.get("/config")
async def config() -> ApiResponse[dict[str, str]]:
    """Public: the Google client id the sign-in button needs."""
    _require_enabled()
    return ApiResponse(data={"googleClientId": settings.google_client_id})


@router.get("/{project_code}/stats")
async def stats(
    _: AdminDep, project: ProjectDep, db: DbSession
) -> ApiResponse[dict[str, Any]]:
    return ApiResponse(data=await admin_stats_service.get_stats(db, project, "ru"))
