from app.schemas.common import Schema


class AreaOut(Schema):
    id: int
    code: str
    name: str
    name_secondary: str | None = None
    descr: str | None
    descr_secondary: str | None = None
    impact: str | None
    impact_secondary: str | None = None
    ord: int


class RegionOut(Schema):
    id: int
    code: str
    name: str
    name_secondary: str | None = None
    descr: str | None
    descr_secondary: str | None = None
    ord: int
    areas: list[AreaOut]
