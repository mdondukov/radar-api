from app.schemas.common import Schema


class StepOut(Schema):
    id: int
    code: str
    name: str
    descr: str | None
    type: str
    next_step_id: int | None
