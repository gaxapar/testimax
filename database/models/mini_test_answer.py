from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MiniTestAnswer(Base):
    __tablename__ = "mini_test_answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str]
    photo_file_id: Mapped[str | None]
    mini_test_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("mini_tests.id"))
