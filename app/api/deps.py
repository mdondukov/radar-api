from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models import Project

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_project(project_code: str, db: DbSession) -> Project:
    project = await db.scalar(
        select(Project).where(Project.code == project_code, Project.is_active.is_(True))
    )
    if project is None:
        raise HTTPException(status_code=404, detail=f"Unknown project '{project_code}'")
    return project


def get_locale(locale: Annotated[str | None, Header()] = None) -> str:
    return locale or settings.default_locale


def get_secondary_locale(
    secondary_locale: Annotated[str | None, Header()] = None,
) -> str | None:
    """Optional mirror language (header `secondary-locale`).

    radar-women shows Kyrgyz alongside Russian, so it asks for both in one
    request. Clients that don't send the header get the response unchanged
    apart from the mirror fields being null.
    """
    return secondary_locale


ProjectDep = Annotated[Project, Depends(get_project)]
LocaleDep = Annotated[str, Depends(get_locale)]
SecondaryLocaleDep = Annotated[str | None, Depends(get_secondary_locale)]
