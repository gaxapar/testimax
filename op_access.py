import asyncio
from dataclasses import dataclass

from maxo import Bot, types
from maxo.errors.api import MaxBotBadRequestError
from maxo.routing.facades import MessageCallbackFacade

from database import DAO, models
from keyboards import callback_payload

OP_TOKEN = "f9LHodD0cOIDw863Ay6jsapTnOWZLZGViAIf3AGQotkqRy42KuPblSKkerbdJpHFKWinPK9MJ0IO5h0wTXhh"


@dataclass(frozen=True)
class OpChannel:
    num: int
    id: int | None
    check: bool
    link: str
    display_link: str


OP_CHANNELS_PHASE1: list[OpChannel] = [
    OpChannel(
        num=3,
        id=-69464283862461,
        check=True,
        link="https://max.ru/mskint",
        display_link="https://max.ru/id503501079307_1_bot?startapp=TL3061b6252c71",
    ),
    OpChannel(
        num=4,
        id=-69274153375165,
        check=True,
        link="https://max.ru/memachh",
        display_link="https://max.ru/memachh",
    ),
    OpChannel(
        num=5,
        id=-71488267686456,
        check=True,
        link="https://max.ru/branding",
        display_link="https://max.ru/id503501079307_1_bot?startapp=TLa2d516cca082",
    ),
]

OP_MESSAGE_TEXT = "<i>Чтобы воспользоваться ботом, подпишитесь на мои каналы</i>"
OP_NOT_CONFIRMED_TEXT = "Подписка не потверждена"

op_bot = Bot(token=OP_TOKEN)
_op_bot_started = False
_op_bot_lock = asyncio.Lock()
_optional_step_seen_users: set[int] = set()


def _has_optional_channels() -> bool:
    return any(not channel.check for channel in OP_CHANNELS_PHASE1)


async def _ensure_op_bot_started() -> bool:
    global _op_bot_started  # noqa: PLW0603

    if _op_bot_started:
        return True

    async with _op_bot_lock:
        if _op_bot_started:
            return True

        try:
            await op_bot.start()
        except Exception:  # noqa: BLE001
            return False

        _op_bot_started = True
        return True


async def _is_member(user_id: int, chat_id: int) -> bool:
    if not await _ensure_op_bot_started():
        return False

    try:
        members_list = await op_bot.get_members(chat_id=chat_id, user_ids=[user_id])
    except Exception:  # noqa: BLE001
        return False

    return bool(members_list.members)


async def _get_checked_followed_channels(user_id: int) -> set[int]:
    followed_channel_nums: set[int] = set()

    for channel in OP_CHANNELS_PHASE1:
        if not channel.check or channel.id is None:
            continue

        if await _is_member(user_id=user_id, chat_id=channel.id):
            followed_channel_nums.add(channel.num)

    return followed_channel_nums


async def build_op_channels_keyboard(user_id: int) -> list[list[types.CallbackButton | types.LinkButton]]:
    followed_checked_channels = await _get_checked_followed_channels(user_id=user_id)

    keyboard: list[list[types.CallbackButton | types.LinkButton]] = []

    for channel in OP_CHANNELS_PHASE1:
        if channel.check and channel.num in followed_checked_channels:
            continue

        keyboard.append(
            [
                types.LinkButton(
                    text="Подписаться",
                    url=channel.display_link or channel.link,
                ),
            ],
        )

    keyboard.append(
        [
            types.CallbackButton(
                text="Проверить",
                payload=callback_payload.OpChannelsCheck().pack(),
            ),
        ],
    )

    return keyboard


async def pass_op_access_if_allowed(user_id: int, dao: DAO) -> bool:
    followed_checked_channels = await _get_checked_followed_channels(user_id=user_id)
    checked_channels = [channel for channel in OP_CHANNELS_PHASE1 if channel.check]
    all_checked_followed = all(channel.num in followed_checked_channels for channel in checked_channels)

    if not all_checked_followed:
        _optional_step_seen_users.discard(user_id)
        return False

    # If all required channels are already followed, keep user one more click
    # on OP screen so optional channels are shown at least once after "Проверить".
    if _has_optional_channels() and user_id not in _optional_step_seen_users:
        _optional_step_seen_users.add(user_id)
        return False

    user = await dao.get_user_by_id(user_id=user_id)
    if not user:
        return False

    user.op_access_granted = True
    dao.add(instance=user)
    await dao.commit()
    _optional_step_seen_users.discard(user_id)

    return True


def optional_step_is_waiting(user_id: int) -> bool:
    return user_id in _optional_step_seen_users


async def is_op_access_required(user: models.User | None) -> bool:
    if user is None:
        return False

    return bool(user.is_op_ref_user and not user.op_access_granted)


async def send_op_access_message(
    user_id: int,
    facade: MessageCallbackFacade,
    warning_text: str | None = None,
) -> None:
    keyboard = await build_op_channels_keyboard(user_id=user_id)
    text = OP_MESSAGE_TEXT

    if warning_text:
        text = f"{text}\n{warning_text}"

    try:
        await facade.edit_message(text=text, keyboard=keyboard)
    except MaxBotBadRequestError as error:
        if "error.edit.invalid.message" not in str(error):
            raise

        await facade.answer_text(text=text, keyboard=keyboard)


async def block_callback_by_op_access(
    user_id: int,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> bool:
    user = await dao.get_user_by_id(user_id=user_id)

    if not await is_op_access_required(user):
        return False

    await send_op_access_message(user_id=user_id, facade=facade)
    return True
