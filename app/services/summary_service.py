from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Project
from app.schemas.summary import SummaryOut, SummaryRequestIn
from app.services.indicator_service import compute_indicators


class StaleAnswersError(Exception):
    """The request names answers this project does not have.

    The only way a real client gets here is a page loaded before the
    questionnaire was re-seeded: it still holds the old answer ids. Scoring
    such a request would silently drop every answer and report zeros, so it is
    refused and the client asks the reader to reload instead.
    """


async def _check_answers_exist(
    db: AsyncSession, project: Project, request: SummaryRequestIn
) -> None:
    answer_ids = {a.answer_id for a in request.answers}
    if not answer_ids:
        return
    known = set(
        (
            await db.scalars(
                select(Answer.id).where(Answer.project_id == project.id, Answer.id.in_(answer_ids))
            )
        ).all()
    )
    if known != answer_ids:
        raise StaleAnswersError(sorted(answer_ids - known))


async def get_summary(
    db: AsyncSession,
    project: Project,
    locale: str,
    request: SummaryRequestIn,
    secondary: str | None = None,
) -> SummaryOut:
    await _check_answers_exist(db, project, request)
    indicators = await compute_indicators(db, project, locale, request.answers, secondary)
    return SummaryOut(indicators=indicators)
