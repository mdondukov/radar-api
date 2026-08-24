from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Question(Base):
    __tablename__ = "question"
    __table_args__ = (UniqueConstraint("project_id", "code", name="question_project_code_uniq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict[str, str]] = mapped_column(JSONB)
    descr: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    is_multi_select: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    ord: Mapped[int] = mapped_column(Integer)


class Answer(Base):
    __tablename__ = "answer"
    __table_args__ = (UniqueConstraint("question_id", "code", name="answer_question_code_uniq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict[str, str]] = mapped_column(JSONB)
    descr: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    weight: Mapped[int] = mapped_column(Integer)
    recommendation: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    ord: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
