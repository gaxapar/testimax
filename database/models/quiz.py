from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .quiz_question import QuizQuestion


class Quiz(Base):
    __tablename__ = "quizes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str]
    photo_file_id: Mapped[str | None]
    creator_user_id: Mapped[int]
    usages: Mapped[int] = mapped_column(default=0)

    questions: Mapped[list[QuizQuestion]] = relationship("QuizQuestion", cascade="all, delete-orphan")
