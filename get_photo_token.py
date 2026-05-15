import asyncio

from maxo import Bot
from maxo.routing import updates
from maxo.routing.dispatcher import Dispatcher
from maxo.routing.facades import MessageCreatedFacade
from maxo.routing.routers.simple import Router
from maxo.transport.long_polling import LongPolling

from config import config

router = Router()


@router.message_created()
async def handler(update: updates.MessageCreated, facade: MessageCreatedFacade):
    if not update.message.body.photo:
        return

    token = update.message.body.photo[-1].payload.token
    await facade.reply(token)


async def main():
    bot = Bot(token=config.bot_token)

    dispatcher = Dispatcher()
    dispatcher.include_router(router=router)

    await LongPolling(dispatcher=dispatcher).start(bot=bot, drop_pending_updates=True)


asyncio.run(main())
