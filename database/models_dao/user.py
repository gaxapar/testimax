from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserDAO:
    session: AsyncSession

    async def get_user_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_passed_op_users_count(self) -> int:
        statement = select(func.count()).select_from(User).where(User.is_op_ref_user, User.op_access_granted)

        result = await self.session.execute(statement)
        return result.scalar_one()
