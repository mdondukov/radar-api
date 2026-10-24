"""Raw material for the admin dashboard of one project.

Everything the dashboard filters on is sent in one response and aggregated in
the browser: the questionnaire (names and texts), the stored submissions, and
the sessions reconstructed from nginx logs before submissions were stored.
Volumes are small (hundreds to a few thousand rows), so this stays cheap.
"""

import json
import re
from functools import cache
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Area, Indicator, Project, Question, Region, Step, Submission
from app.services.i18n import localize_required

LOG_HISTORY_PATH = Path(__file__).parent.parent / "data" / "log_history.json"
MOBILE = re.compile(r"Mobile|Android|iPhone|iPad", re.IGNORECASE)


@cache
def _log_history() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(LOG_HISTORY_PATH.read_text())
    return data


def _device(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    return "mobile" if MOBILE.search(user_agent) else "desktop"


async def get_stats(db: AsyncSession, project: Project, locale: str) -> dict[str, Any]:
    default = project.default_locale

    def text(value: dict[str, str] | None) -> str:
        return localize_required(value or {}, locale, default) if value else ""

    steps = {
        s.id: s.code
        for s in (await db.scalars(select(Step).where(Step.project_id == project.id))).all()
    }
    questions = (
        await db.scalars(
            select(Question).where(Question.project_id == project.id).order_by(Question.ord)
        )
    ).all()
    answers = (
        await db.scalars(select(Answer).where(Answer.project_id == project.id).order_by(Answer.ord))
    ).all()
    answers_by_question: dict[int, list[Answer]] = {}
    for a in answers:
        answers_by_question.setdefault(a.question_id, []).append(a)
    questions_by_step: dict[int, list[Question]] = {}
    for q in questions:
        questions_by_step.setdefault(q.step_id, []).append(q)

    indicators = (
        await db.scalars(
            select(Indicator)
            .where(Indicator.project_id == project.id, Indicator.is_active.is_(True))
            .order_by(Indicator.ord)
        )
    ).all()

    regions = (
        await db.scalars(
            select(Region).where(Region.project_id == project.id).order_by(Region.ord)
        )
    ).all()
    areas = (
        await db.scalars(select(Area).where(Area.project_id == project.id).order_by(Area.ord))
    ).all()

    submissions = (
        await db.scalars(
            select(Submission)
            .where(Submission.project_code == project.code)
            .order_by(Submission.created_at)
        )
    ).all()

    return {
        "indicators": [
            {
                "code": i.code,
                "step_code": steps[i.step_id],
                "name": text(i.name),
                "ord": i.ord,
                "high_risk_max": float(i.high_risk_max) if i.high_risk_max is not None else None,
                "medium_risk_max": (
                    float(i.medium_risk_max) if i.medium_risk_max is not None else None
                ),
                "questions": [
                    {
                        "code": q.code,
                        "content": text(q.content),
                        "ord": q.ord,
                        "is_multi_select": q.is_multi_select,
                        "answers": [
                            {
                                "code": a.code,
                                "content": text(a.content),
                                "weight": a.weight,
                                "ord": a.ord,
                            }
                            for a in answers_by_question.get(q.id, [])
                        ],
                    }
                    for q in questions_by_step.get(i.step_id, [])
                ],
            }
            for i in indicators
        ],
        "regions": [
            {
                "code": r.code,
                "name": text(r.name),
                "areas": [
                    {"code": a.code, "name": text(a.name)} for a in areas if a.region_id == r.id
                ],
            }
            for r in regions
        ],
        "submissions": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(),
                "session_id": s.session_id,
                "source": s.source,
                "is_complete": s.is_complete,
                "locale": s.locale,
                "device": _device(s.user_agent),
                "region_code": s.region_code,
                "area_code": s.area_code,
                "answers": [[a["question_code"], a["answer_code"]] for a in s.answers],
                "indicators": {i["code"]: [i["value"], i["risk_zone"]] for i in s.indicators},
            }
            for s in submissions
        ],
        "log_history": _log_history(),
    }
