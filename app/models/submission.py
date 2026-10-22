from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Submission(Base):
    """One POST /summary call, kept for statistics.

    Anonymous by design: no IP and nothing the reader typed, only what they
    picked. Answers and indicators are stored by code alongside the ids and
    weights of the moment, so a record stays readable after the content is
    edited. A project row going away keeps its submissions (SET NULL).
    """

    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("project.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_code: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    # random id the page generates once per load: links a reader's block
    # results to their radar without identifying them
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    # "step" - result page of one block, "radar" - the final radar
    source: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # every question of every indicator answered
    is_complete: Mapped[bool] = mapped_column(Boolean)
    locale: Mapped[str] = mapped_column(String(8))
    secondary_locale: Mapped[str | None] = mapped_column(String(8), nullable=True)
    region_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    region_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    area_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    area_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # [{step_code, question_code, answer_code, answer_id, weight}]
    answers: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    # [{code, value, risk_zone}]
    indicators: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
