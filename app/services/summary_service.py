from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.schemas.summary import SummaryOut, SummaryRequestIn
from app.services.indicator_service import compute_indicators


async def get_summary(
    db: AsyncSession, project: Project, locale: str, request: SummaryRequestIn
) -> SummaryOut:
    indicators = await compute_indicators(db, project, locale, request.answers)
    return SummaryOut(indicators=indicators)
