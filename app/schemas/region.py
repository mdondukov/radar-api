from app.schemas.common import Schema


class AreaOut(Schema):
    id: int
    code: str
    name: str
    descr: str | None
    impact: str | None
    ord: int


class RegionOut(Schema):
    id: int
    code: str
    name: str
    descr: str | None
    ord: int
    areas: list[AreaOut]
