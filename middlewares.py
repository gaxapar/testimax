from typing import Any

from maxo import Ctx
from maxo.routing.interfaces.middleware import BaseMiddleware, NextMiddleware
from maxo.routing.updates import BotStarted, MessageCallback, MessageCreated

from database import DAO, DatabaseManager


class DatabaseMiddleware(BaseMiddleware[BotStarted | MessageCreated | MessageCallback]):
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    async def __call__(
        self,
        update: BotStarted | MessageCreated | MessageCallback,  # noqa: ARG002
        ctx: Ctx,
        next: NextMiddleware[MessageCreated | MessageCallback],  # noqa: A002
    ) -> Any:  # noqa: ANN401
        dao = DAO(session=self.database_manager.session())

        ctx["dao"] = dao

        try:
            return await next(ctx)

        finally:
            await dao.close()
