import enum

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StepType(enum.StrEnum):
    REGION = "REGION"
    ASSESSMENT = "ASSESSMENT"
    RADAR = "RADAR"


class Step(Base):
    __tablename__ = "step"
    __table_args__ = (UniqueConstraint("project_id", "code", name="step_project_code_uniq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[dict[str, str]] = mapped_column(JSONB)
    descr: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    type: Mapped[StepType] = mapped_column(SqlEnum(StepType, name="step_type"))
    next_step_id: Mapped[int | None] = mapped_column(ForeignKey("step.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    ord: Mapped[int] = mapped_column(Integer)
