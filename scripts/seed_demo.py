"""Insert a minimal demo project so the API can be smoke-tested by hand.

Usage: uv run python scripts/seed_demo.py
"""

import asyncio

from app.core.db import SessionLocal
from app.models import Answer, Indicator, Project, Question, Step
from app.models.step import StepType


async def main() -> None:
    async with SessionLocal() as db:
        project = Project(code="demo", name="Demo project", default_locale="ru")
        db.add(project)
        await db.flush()

        step = Step(
            project_id=project.id,
            code="env",
            name={"ru": "Окружающая среда"},
            type=StepType.ASSESSMENT,
            ord=1,
        )
        radar_step = Step(
            project_id=project.id, code="radar", name={"ru": "Радар"}, type=StepType.RADAR, ord=2
        )
        db.add_all([step, radar_step])
        await db.flush()

        question = Question(
            project_id=project.id,
            step_id=step.id,
            code="lakes",
            content={"ru": "Наличие озёр"},
            ord=1,
        )
        db.add(question)
        await db.flush()

        answers = [
            Answer(
                project_id=project.id,
                question_id=question.id,
                code="none",
                content={"ru": "Нет"},
                weight=0,
                recommendation={"ru": "Высадить лесополосы вдоль берегов."},
                ord=1,
            ),
            Answer(
                project_id=project.id,
                question_id=question.id,
                code="good",
                content={"ru": "Есть, в хорошем состоянии"},
                weight=3,
                ord=2,
            ),
        ]
        db.add_all(answers)
        await db.flush()

        indicator = Indicator(
            project_id=project.id,
            step_id=step.id,
            code="env",
            name={"ru": "Окружающая среда"},
            ord=1,
            high_risk_max=1,
            medium_risk_max=2,
            high_risk_text={"ru": "Высокий риск: требуется вмешательство."},
            medium_risk_text={"ru": "Средний риск: нужны улучшения."},
            low_risk_text={"ru": "Низкий риск: поддерживающий уход."},
        )
        db.add(indicator)

        await db.commit()
        print(f"seeded project code={project.code!r}, answer ids={[a.id for a in answers]}")


if __name__ == "__main__":
    asyncio.run(main())
