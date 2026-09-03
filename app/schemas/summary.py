from typing import Literal

from app.schemas.common import Schema


class AnswerSelectIn(Schema):
    step_id: int
    question_id: int
    answer_id: int


class RegionSelectIn(Schema):
    region_id: int
    area_id: int


class SummaryRequestIn(Schema):
    region: RegionSelectIn | None = None
    answers: list[AnswerSelectIn]


class IndicatorOut(Schema):
    code: str
    step_id: int
    name: str
    name_secondary: str | None = None
    value: float
    risk_zone: Literal["high", "medium", "low"]
    risk_text: str | None
    risk_text_secondary: str | None = None


class SummaryOut(Schema):
    indicators: list[IndicatorOut]
