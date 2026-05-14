from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MiniTestAnswer


class MiniTestAnswerDAO:
    session: AsyncSession

    async def get_mini_test_answer_by_id(self, mini_test_answer_id: int) -> MiniTestAnswer | None:
        statement = select(MiniTestAnswer).where(MiniTestAnswer.id == mini_test_answer_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_answers_by_mini_test_id(self, mini_test_id: int) -> Sequence[MiniTestAnswer]:
        statement = select(MiniTestAnswer).where(MiniTestAnswer.mini_test_id == mini_test_id)

        result = await self.session.execute(statement)
        return result.scalars().all()
