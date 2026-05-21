from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReferralStats(Base):
    __tablename__ = "referral_stats"

    slug: Mapped[str] = mapped_column(primary_key=True)
    new_users_count: Mapped[int] = mapped_column(default=0)
    old_users_count: Mapped[int] = mapped_column(default=0)
