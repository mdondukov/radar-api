from collections import defaultdict
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Indicator, Project
from app.schemas.summary import AnswerSelectIn, IndicatorOut
from app.services.i18n import localize, localize_required, localize_secondary

RiskZone = Literal["high", "medium", "low"]


def _risk_zone(indicator: Indicator, value: float) -> RiskZone:
    if indicator.high_risk_max is not None and value <= float(indicator.high_risk_max):
        return "high"
    if indicator.medium_risk_max is not None and value <= float(indicator.medium_risk_max):
        return "medium"
    return "low"


def _risk_text_source(indicator: Indicator, zone: RiskZone) -> dict[str, str] | None:
    return {
        "high": indicator.high_risk_text,
        "medium": indicator.medium_risk_text,
        "low": indicator.low_risk_text,
    }[zone]


def _risk_text(
    indicator: Indicator, zone: RiskZone, locale: str, default_locale: str
) -> str | None:
    return localize(_risk_text_source(indicator, zone), locale, default_locale)


async def compute_indicators(
    db: AsyncSession,
    project: Project,
    locale: str,
    answers: list[AnswerSelectIn],
    secondary: str | None = None,
) -> list[IndicatorOut]:
    indicators = (
        await db.scalars(
            select(Indicator)
            .where(Indicator.project_id == project.id, Indicator.is_active.is_(True))
            .order_by(Indicator.ord)
        )
    ).all()

    answer_ids_by_step: dict[int, list[int]] = defaultdict(list)
    for select_ in answers:
        answer_ids_by_step[select_.step_id].append(select_.answer_id)

    all_answer_ids = {aid for ids in answer_ids_by_step.values() for aid in ids}
    weight_by_answer_id: dict[int, int] = {}
    if all_answer_ids:
        rows = (
            await db.scalars(select(Answer).where(Answer.id.in_(all_answer_ids)))
        ).all()
        weight_by_answer_id = {a.id: a.weight for a in rows}

    result: list[IndicatorOut] = []
    for indicator in indicators:
        answer_ids = answer_ids_by_step.get(indicator.step_id, [])
        weights = [weight_by_answer_id[aid] for aid in answer_ids if aid in weight_by_answer_id]
        value = round((sum(weights) / len(weights)) * 10) / 10 if weights else 0.0

        zone = _risk_zone(indicator, value)
        result.append(
            IndicatorOut(
                code=indicator.code,
                step_id=indicator.step_id,
                name=localize_required(indicator.name, locale, project.default_locale),
                name_secondary=localize_secondary(indicator.name, secondary),
                value=value,
                risk_zone=zone,
                risk_text=_risk_text(indicator, zone, locale, project.default_locale),
                risk_text_secondary=localize_secondary(
                    _risk_text_source(indicator, zone), secondary
                ),
            )
        )

    return result
