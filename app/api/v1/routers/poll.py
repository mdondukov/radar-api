from fastapi import APIRouter

from app.api.deps import DbSession, LocaleDep, ProjectDep, SecondaryLocaleDep
from app.schemas.common import ApiResponse
from app.schemas.question import QuestionOut
from app.schemas.region import RegionOut
from app.schemas.step import StepOut
from app.schemas.summary import SummaryOut, SummaryRequestIn
from app.services import poll_service, summary_service

router = APIRouter(prefix="/v1/{project_code}/poll", tags=["poll"])


@router.get("/steps")
async def steps(
    project: ProjectDep, locale: LocaleDep, secondary: SecondaryLocaleDep, db: DbSession
) -> ApiResponse[list[StepOut]]:
    return ApiResponse(data=await poll_service.get_steps(db, project, locale, secondary))


@router.get("/regions")
async def regions(
    project: ProjectDep, locale: LocaleDep, secondary: SecondaryLocaleDep, db: DbSession
) -> ApiResponse[list[RegionOut]]:
    return ApiResponse(data=await poll_service.get_regions(db, project, locale, secondary))


@router.get("/assessment")
async def assessment(
    project: ProjectDep, locale: LocaleDep, secondary: SecondaryLocaleDep, db: DbSession
) -> ApiResponse[list[QuestionOut]]:
    return ApiResponse(data=await poll_service.get_questions(db, project, locale, secondary))


@router.post("/summary")
async def summary(
    request: SummaryRequestIn,
    project: ProjectDep,
    locale: LocaleDep,
    secondary: SecondaryLocaleDep,
    db: DbSession,
) -> ApiResponse[SummaryOut]:
    return ApiResponse(
        data=await summary_service.get_summary(db, project, locale, request, secondary)
    )
