from pydantic import BaseModel


class AnswerOut(BaseModel):
    id: int
    code: str
    content: str
    weight: int
    recommendation: str | None
    ord: int


class QuestionOut(BaseModel):
    id: int
    step_id: int
    code: str
    content: str
    descr: str | None
    is_multi_select: bool
    answers: list[AnswerOut]
