from collections.abc import Sequence
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Quiz

PAGE_SIZE = 10


class QuizDAO:
    session: AsyncSession

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz | None:
        statement = select(Quiz).where(Quiz.id == quiz_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_quizzes_by_user_id(self, user_id: int) -> Sequence[Quiz]:
        statement = select(Quiz).where(Quiz.creator_user_id == user_id)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_quiz_place_in_top(self, quiz_id: int) -> int:
        statement = select(Quiz.id).order_by(Quiz.usages.desc())

        result = await self.session.execute(statement)
        quiz_ids = result.scalars().all()

        return quiz_ids.index(quiz_id) + 1 if quiz_id in quiz_ids else len(quiz_ids) + 1

    async def get_random_quiz(self) -> Quiz | None:
        statement = select(Quiz).where(Quiz.is_active).order_by(func.random()).limit(1)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_quizzes_page(self, page: int) -> Sequence[Quiz]:
        statement = (
            select(Quiz)
            .where(Quiz.is_active)
            .order_by(Quiz.usages.desc(), Quiz.id.asc())
            .offset((page - 1) * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_quizzes_pages_count(self) -> int:
        statement = select(func.count()).select_from(Quiz).where(Quiz.is_active)

        result = await self.session.execute(statement)
        return ceil(result.scalar_one() / PAGE_SIZE)

    async def get_draft_quizzes_by_user_id(self, user_id: int) -> Sequence[Quiz]:
        """Get all draft (inactive) quizzes created by user."""
        statement = select(Quiz).where(
            Quiz.creator_user_id == user_id,
            ~Quiz.is_active,
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_all_draft_quizzes(self) -> Sequence[Quiz]:
        """Get all draft (inactive) quizzes for admin review."""
        statement = select(Quiz).where(~Quiz.is_active).order_by(Quiz.id.desc())

        result = await self.session.execute(statement)
        return result.scalars().all()
