from typing import Literal

from pydantic import BaseModel


class AnswerSelectIn(BaseModel):
    step_id: int
    question_id: int
    answer_id: int


class SummaryRequestIn(BaseModel):
    region_id: int | None = None
    area_id: int | None = None
    answers: list[AnswerSelectIn]


class IndicatorOut(BaseModel):
    code: str
    name: str
    value: float
    risk_zone: Literal["high", "medium", "low"]
    risk_text: str | None


class SummaryOut(BaseModel):
    indicators: list[IndicatorOut]
