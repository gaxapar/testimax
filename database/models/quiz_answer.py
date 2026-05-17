from sqlalchemy import BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class QuizAnswer(Base):
    __tablename__ = "quizes_answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str]
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("quizes_questions.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
