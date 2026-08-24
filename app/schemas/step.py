from pydantic import BaseModel


class StepOut(BaseModel):
    id: int
    code: str
    name: str
    descr: str | None
    type: str
    next_step_id: int | None
