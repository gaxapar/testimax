from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import QuizAnswer


class QuizAnswerDAO:
    session: AsyncSession

    async def get_answer_by_id(self, answer_id: int) -> QuizAnswer | None:
        statement = select(QuizAnswer).where(QuizAnswer.id == answer_id)

        result = await self.session.execute(statement)
        return result.scalar()

    async def get_answers_by_question_id(self, question_id: int) -> Sequence[QuizAnswer]:
        statement = select(QuizAnswer).where(QuizAnswer.question_id == question_id).order_by(QuizAnswer.id.asc())

        result = await self.session.execute(statement)
        return result.scalars().all()
