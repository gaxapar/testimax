from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .quiz_answer import QuizAnswer


class QuizQuestion(Base):
    __tablename__ = "quizes_questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str]
    photo_file_id: Mapped[str | None]
    quiz_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("quizes.id"))

    answers: Mapped[list[QuizAnswer]] = relationship("QuizAnswer", cascade="all, delete-orphan")
