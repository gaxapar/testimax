from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ReferralStats


class ReferralStatsDAO:
    session: AsyncSession

    async def get_referral_stats_by_slug(self, slug: str) -> ReferralStats | None:
        statement = select(ReferralStats).where(ReferralStats.slug == slug)

        result = await self.session.execute(statement)
        return result.scalar()
