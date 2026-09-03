from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Indicator, Project, Question, Step
from app.models.step import StepType

_counter = 0


def _unique(prefix: str) -> str:
    global _counter
    _counter += 1
    return f"{prefix}-{_counter}"


async def make_project(db: AsyncSession, *, default_locale: str = "ru") -> Project:
    project = Project(code=_unique("project"), name="Test project", default_locale=default_locale)
    db.add(project)
    await db.flush()
    return project


async def make_step(
    db: AsyncSession, project: Project, *, type_: StepType = StepType.ASSESSMENT, ord: int = 1
) -> Step:
    step = Step(
        project_id=project.id,
        code=_unique("step"),
        name={"ru": "Шаг"},
        type=type_,
        ord=ord,
    )
    db.add(step)
    await db.flush()
    return step


async def make_indicator(
    db: AsyncSession,
    project: Project,
    step: Step,
    *,
    high_risk_max: float | None = None,
    medium_risk_max: float | None = None,
) -> Indicator:
    indicator = Indicator(
        project_id=project.id,
        step_id=step.id,
        code=_unique("indicator"),
        name={"ru": "Индикатор"},
        ord=1,
        high_risk_max=high_risk_max,
        medium_risk_max=medium_risk_max,
        high_risk_text={"ru": "high risk"} if high_risk_max is not None else None,
        medium_risk_text={"ru": "medium risk"} if medium_risk_max is not None else None,
        low_risk_text={"ru": "low risk"},
    )
    db.add(indicator)
    await db.flush()
    return indicator


async def make_question(
    db: AsyncSession,
    project: Project,
    step: Step,
    *,
    is_multi_select: bool = False,
    content: dict[str, str] | None = None,
) -> Question:
    question = Question(
        project_id=project.id,
        step_id=step.id,
        code=_unique("question"),
        content=content or {"ru": "Вопрос"},
        is_multi_select=is_multi_select,
        ord=1,
    )
    db.add(question)
    await db.flush()
    return question


async def make_answer(
    db: AsyncSession,
    project: Project,
    question: Question,
    *,
    weight: int,
    ord: int = 1,
    recommendation: dict[str, str] | None = None,
    content: dict[str, str] | None = None,
) -> Answer:
    answer = Answer(
        project_id=project.id,
        question_id=question.id,
        code=_unique("answer"),
        content=content or {"ru": f"weight {weight}"},
        weight=weight,
        ord=ord,
        recommendation=recommendation,
    )
    db.add(answer)
    await db.flush()
    return answer
