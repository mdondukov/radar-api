import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Area, Indicator, Project, Question, Region, Step, Submission
from app.schemas.summary import IndicatorOut, SummaryRequestIn

logger = logging.getLogger("radar_api")

USER_AGENT_MAX = 512


async def record(
    db: AsyncSession,
    project: Project,
    request: SummaryRequestIn,
    indicators: list[IndicatorOut],
    locale: str,
    secondary: str | None,
    user_agent: str | None,
) -> None:
    """Store one summary call for statistics.

    Never lets a failure reach the reader: the radar matters more than the
    record of it, so any error is logged and rolled back.
    """
    try:
        db.add(
            await _build(db, project, request, indicators, locale, secondary, user_agent)
        )
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("could not store a submission")


async def _build(
    db: AsyncSession,
    project: Project,
    request: SummaryRequestIn,
    indicators: list[IndicatorOut],
    locale: str,
    secondary: str | None,
    user_agent: str | None,
) -> Submission:
    answer_ids = {a.answer_id for a in request.answers}
    rows = (
        await db.execute(
            select(Answer.id, Answer.code, Answer.weight, Question.code, Step.code)
            .join(Question, Question.id == Answer.question_id)
            .join(Step, Step.id == Question.step_id)
            .where(Answer.project_id == project.id, Answer.id.in_(answer_ids))
        )
    ).all()
    by_id = {r[0]: r for r in rows}
    answers = [
        {
            "step_code": by_id[a.answer_id][4],
            "question_code": by_id[a.answer_id][3],
            "answer_code": by_id[a.answer_id][1],
            "answer_id": a.answer_id,
            "weight": by_id[a.answer_id][2],
        }
        for a in request.answers
        if a.answer_id in by_id
    ]

    indicator_steps = select(Indicator.step_id).where(
        Indicator.project_id == project.id, Indicator.is_active.is_(True)
    )
    question_count = await db.scalar(
        select(func.count())
        .select_from(Question)
        .where(Question.step_id.in_(indicator_steps), Question.is_active.is_(True))
    )
    answered = {a["question_code"] for a in answers}

    region_code = area_code = None
    if request.region is not None:
        region_code = await db.scalar(
            select(Region.code).where(
                Region.project_id == project.id, Region.id == request.region.region_id
            )
        )
        area_code = await db.scalar(
            select(Area.code).where(
                Area.project_id == project.id, Area.id == request.region.area_id
            )
        )

    return Submission(
        project_id=project.id,
        project_code=project.code,
        session_id=request.session_id,
        device_id=request.device_id,
        source=request.source,
        is_complete=bool(question_count) and len(answered) >= (question_count or 0),
        locale=locale,
        secondary_locale=secondary,
        region_id=request.region.region_id if request.region else None,
        region_code=region_code,
        area_id=request.region.area_id if request.region else None,
        area_code=area_code,
        answers=answers,
        indicators=[
            {"code": i.code, "value": i.value, "risk_zone": i.risk_zone} for i in indicators
        ],
        user_agent=user_agent[:USER_AGENT_MAX] if user_agent else None,
    )
