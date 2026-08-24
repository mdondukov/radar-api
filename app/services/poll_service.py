from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Area, Project, Question, Region, Step
from app.schemas.question import AnswerOut, QuestionOut
from app.schemas.region import AreaOut, RegionOut
from app.schemas.step import StepOut
from app.services.i18n import localize, localize_required


async def get_steps(db: AsyncSession, project: Project, locale: str) -> list[StepOut]:
    stmt = (
        select(Step)
        .where(Step.project_id == project.id, Step.is_active.is_(True))
        .order_by(Step.ord)
    )
    steps = (await db.scalars(stmt)).all()
    return [
        StepOut(
            id=s.id,
            code=s.code,
            name=localize_required(s.name, locale, project.default_locale),
            intro=localize(s.intro, locale, project.default_locale),
            descr=localize(s.descr, locale, project.default_locale),
            type=s.type.value,
            next_step_id=s.next_step_id,
        )
        for s in steps
    ]


async def get_regions(db: AsyncSession, project: Project, locale: str) -> list[RegionOut]:
    regions = (
        await db.scalars(
            select(Region)
            .where(Region.project_id == project.id, Region.is_active.is_(True))
            .order_by(Region.ord)
        )
    ).all()
    areas = (
        await db.scalars(
            select(Area)
            .where(Area.project_id == project.id, Area.is_active.is_(True))
            .order_by(Area.ord)
        )
    ).all()

    areas_by_region: dict[int, list[Area]] = {}
    for area in areas:
        areas_by_region.setdefault(area.region_id, []).append(area)

    return [
        RegionOut(
            id=region.id,
            code=region.code,
            name=localize_required(region.name, locale, project.default_locale),
            descr=localize(region.descr, locale, project.default_locale),
            areas=[
                AreaOut(
                    id=a.id,
                    code=a.code,
                    name=localize_required(a.name, locale, project.default_locale),
                    descr=localize(a.descr, locale, project.default_locale),
                    impact=localize(a.impact, locale, project.default_locale),
                    ord=a.ord,
                )
                for a in areas_by_region.get(region.id, [])
            ],
        )
        for region in regions
    ]


async def get_questions(db: AsyncSession, project: Project, locale: str) -> list[QuestionOut]:
    questions = (
        await db.scalars(
            select(Question)
            .where(Question.project_id == project.id, Question.is_active.is_(True))
            .order_by(Question.ord)
        )
    ).all()
    answers = (
        await db.scalars(
            select(Answer)
            .where(Answer.project_id == project.id, Answer.is_active.is_(True))
            .order_by(Answer.ord)
        )
    ).all()

    answers_by_question: dict[int, list[Answer]] = {}
    for answer in answers:
        answers_by_question.setdefault(answer.question_id, []).append(answer)

    return [
        QuestionOut(
            id=q.id,
            step_id=q.step_id,
            code=q.code,
            content=localize_required(q.content, locale, project.default_locale),
            descr=localize(q.descr, locale, project.default_locale),
            is_multi_select=q.is_multi_select,
            answers=[
                AnswerOut(
                    id=a.id,
                    code=a.code,
                    content=localize_required(a.content, locale, project.default_locale),
                    descr=localize(a.descr, locale, project.default_locale),
                    weight=a.weight,
                    recommendation=localize(a.recommendation, locale, project.default_locale),
                    ord=a.ord,
                )
                for a in answers_by_question.get(q.id, [])
            ],
        )
        for q in questions
    ]
