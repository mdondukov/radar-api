from pydantic import BaseModel


class AreaOut(BaseModel):
    id: int
    code: str
    name: str
    descr: str | None
    impact: str | None
    ord: int


class RegionOut(BaseModel):
    id: int
    code: str
    name: str
    areas: list[AreaOut]
