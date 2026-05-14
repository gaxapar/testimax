import asyncio
import logging
from contextlib import suppress
from typing import Any, Self, TypedDict

from maxo import Bot

logger = logging.getLogger(__name__)


class MiniTestAnswer(TypedDict):
    text: str
    photo_file_id: str | None


class SendActionLoop:
    def __init__(self, bot: Bot, interval: float = 3.0, **send_action_kwargs: Any) -> None:  # noqa: ANN401
        self.bot = bot
        self.interval = interval
        self.send_action_kwargs = send_action_kwargs
        self._task: asyncio.Task[None] | None = None

    async def _run(self) -> None:
        while True:
            try:
                await self.bot.send_action(**self.send_action_kwargs)
            except Exception:
                logger.exception("Failed to send chat action")

            await asyncio.sleep(self.interval)

    async def __aenter__(self) -> Self:
        self._task = asyncio.create_task(self._run())

        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._task is None:
            return

        self._task.cancel()

        with suppress(asyncio.CancelledError):
            await self._task


async def is_subbed(bot: Bot, user_id: int, channels: list[dict[str, int]]) -> bool:
    for channel in channels:
        members_list = await bot.get_members(chat_id=channel["id"], user_ids=[user_id])

        if not members_list.members:
            return False

    return True
