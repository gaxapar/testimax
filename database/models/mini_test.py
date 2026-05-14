from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mini_test_answer import MiniTestAnswer


class MiniTest(Base):
    __tablename__ = "mini_tests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str]
    photo_file_id: Mapped[str | None]
    creator_user_id: Mapped[int]
    usages: Mapped[int] = mapped_column(default=0)
    answers: Mapped[list[MiniTestAnswer]] = relationship("MiniTestAnswer", cascade="all, delete-orphan")
