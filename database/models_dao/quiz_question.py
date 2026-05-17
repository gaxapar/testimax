from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import QuizQuestion


class QuizQuestionDAO:
    session: AsyncSession

    async def get_question_by_id(self, question_id: int) -> QuizQuestion | None:
        statement = select(QuizQuestion).where(QuizQuestion.id == question_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_questions_by_quiz_id(self, quiz_id: int) -> Sequence[QuizQuestion]:
        statement = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)

        result = await self.session.execute(statement)
        return result.scalars().all()
