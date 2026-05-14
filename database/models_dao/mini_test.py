from collections.abc import Sequence
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MiniTest

PAGE_SIZE = 10


class MiniTestDAO:
    session: AsyncSession

    async def get_mini_test_by_id(self, mini_test_id: int) -> MiniTest | None:
        statement = select(MiniTest).where(MiniTest.id == mini_test_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_mini_tests_by_user_id(self, user_id: int) -> Sequence[MiniTest]:
        statement = select(MiniTest).where(MiniTest.creator_user_id == user_id)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_mini_test_place_in_top(self, mini_test_id: int) -> int:
        statement = select(MiniTest.id).order_by(MiniTest.usages.desc())

        result = await self.session.execute(statement)
        mini_test_ids = result.scalars().all()

        return mini_test_ids.index(mini_test_id) + 1 if mini_test_id in mini_test_ids else len(mini_test_ids) + 1

    async def get_random_mini_test(self) -> MiniTest | None:
        statement = select(MiniTest).order_by(func.random()).limit(1)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_mini_tests_page(self, page: int) -> Sequence[MiniTest]:
        statement = (
            select(MiniTest)
            .order_by(MiniTest.usages.desc(), MiniTest.id.asc())
            .offset((page - 1) * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_mini_tests_pages_count(self) -> int:
        statement = select(func.count()).select_from(MiniTest)

        result = await self.session.execute(statement)
        return ceil(result.scalar_one() / PAGE_SIZE)
