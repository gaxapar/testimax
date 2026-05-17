import asyncio
import json
from pathlib import Path
from typing import Any

from maxo import Bot
from maxo.bot.defaults import BotDefaults
from maxo.enums import TextFormat
from maxo.routing.dispatcher import Dispatcher
from maxo.transport.long_polling import LongPolling
from redis.asyncio import Redis

import handlers
from config import config
from database import DatabaseManager
from middlewares import DatabaseMiddleware

here = Path(__file__).parent

with Path.open(here / "channels.json") as file:
    channels: list[dict[str, Any]] = json.load(file)


async def main():
    database_manager = DatabaseManager(
        user=config.db_user,
        password=config.db_password,
        db_name=config.db_name,
        host=config.db_host,
    )

    bot = Bot(token=config.bot_token, defaults=BotDefaults(text_format=TextFormat.HTML))

    redis = Redis()

    dispatcher = Dispatcher(workflow_data={"redis": redis})
    dispatcher.include_router(router=handlers.router)

    dispatcher.bot_started.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]
    dispatcher.message_created.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]
    dispatcher.message_callback.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]

    await LongPolling(dispatcher=dispatcher).start(bot=bot, drop_pending_updates=True)


asyncio.run(main())
