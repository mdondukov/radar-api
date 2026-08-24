from app.schemas.common import Schema


class AnswerOut(Schema):
    id: int
    code: str
    content: str
    descr: str | None
    weight: int
    recommendation: str | None
    ord: int


class QuestionOut(Schema):
    id: int
    step_id: int
    code: str
    content: str
    descr: str | None
    is_multi_select: bool
    answers: list[AnswerOut]
