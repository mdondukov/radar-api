from app.schemas.common import Schema


class AnswerOut(Schema):
    id: int
    code: str
    content: str
    content_secondary: str | None = None
    descr: str | None
    descr_secondary: str | None = None
    weight: int
    recommendation: str | None
    recommendation_secondary: str | None = None
    ord: int


class QuestionOut(Schema):
    id: int
    step_id: int
    code: str
    content: str
    content_secondary: str | None = None
    descr: str | None
    descr_secondary: str | None = None
    is_multi_select: bool
    answers: list[AnswerOut]
