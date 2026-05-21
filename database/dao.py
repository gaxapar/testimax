from sqlalchemy.ext.asyncio import AsyncSession

from .models import AnyModel
from .models_dao import MiniTestAnswerDAO, MiniTestDAO, QuizAnswerDAO, QuizDAO, QuizQuestionDAO, ReferralStatsDAO, UserDAO


class DAO(MiniTestAnswerDAO, MiniTestDAO, UserDAO, QuizDAO, QuizQuestionDAO, QuizAnswerDAO, ReferralStatsDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, instance: AnyModel) -> None:
        self.session.add(instance=instance)

    async def delete(self, instance: AnyModel) -> None:
        await self.session.delete(instance=instance)

    async def commit(self) -> None:
        await self.session.commit()

    async def close(self) -> None:
        await self.session.close()
