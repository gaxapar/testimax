from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    name: Mapped[str | None]
    is_op_ref_user: Mapped[bool] = mapped_column(default=False)
    op_access_granted: Mapped[bool] = mapped_column(default=False)
