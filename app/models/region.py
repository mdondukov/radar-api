from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Region(Base):
    __tablename__ = "region"
    __table_args__ = (UniqueConstraint("project_id", "code", name="region_project_code_uniq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[dict[str, str]] = mapped_column(JSONB)
    descr: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    ord: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Area(Base):
    __tablename__ = "area"
    __table_args__ = (UniqueConstraint("region_id", "code", name="area_region_code_uniq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[dict[str, str]] = mapped_column(JSONB)
    descr: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    impact: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    ord: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
