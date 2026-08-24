from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Indicator(Base):
    """One radar axis. Its value is the flat average weight of all selected
    answers whose AnswerSelect.step_id matches this indicator's step_id."""

    __tablename__ = "indicator"
    __table_args__ = (
        UniqueConstraint("project_id", "code", name="indicator_project_code_uniq"),
        UniqueConstraint("step_id", name="indicator_step_uniq"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[dict[str, str]] = mapped_column(JSONB)
    ord: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    scale_min: Mapped[int] = mapped_column(Integer, default=0)
    scale_max: Mapped[int] = mapped_column(Integer, default=3)

    # Upper bound (inclusive) of the raw average value for each risk band.
    # value <= high_risk_max          -> high risk
    # high_risk_max < value <= medium_risk_max -> medium risk
    # value > medium_risk_max         -> low risk
    high_risk_max: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    medium_risk_max: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)

    high_risk_text: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    medium_risk_text: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    low_risk_text: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
