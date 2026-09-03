from app.schemas.common import Schema


class StepOut(Schema):
    id: int
    code: str
    name: str
    name_secondary: str | None = None
    intro: str | None
    intro_secondary: str | None = None
    descr: str | None
    descr_secondary: str | None = None
    type: str
    next_step_id: int | None
