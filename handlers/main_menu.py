from maxo import types
from maxo.routing import filters, updates
from maxo.routing.facades import BotStartedFacade, MessageCreatedFacade
from maxo.routing.filters.command import CommandObject
from maxo.routing.routers.simple import Router

import keyboards
import texts
from database import DAO, models

router = Router()


@router.bot_started()
async def handle_bot_start(update: updates.BotStarted, facade: BotStartedFacade, dao: DAO) -> None:
    user_id = update.user.user_id

    user = await dao.get_user_by_id(user_id=user_id)

    if not user:
        user = models.User(id=user_id, username=update.user.username, name=update.user.full_name)

        dao.add(instance=user)
        await dao.commit()

    if update.payload and update.unsafe_payload.isdigit():
        mini_test_id = int(update.unsafe_payload)

        mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

        media = None

        if mini_test.photo_file_id:
            media = [
                types.PhotoAttachmentRequest(
                    payload=types.PhotoAttachmentRequestPayload(token=mini_test.photo_file_id),
                ),
            ]

        keyboard = keyboards.proceed_mini_test(mini_test_id=mini_test_id)
        await facade.send_message(text=mini_test.title, media=media, keyboard=keyboard)

        return

    await facade.send_message(text=texts.start.format(full_name=user.name))
    await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)


@router.message_created(filters.CommandStart())
async def handle_start_command(
    update: updates.MessageCreated,
    command: CommandObject,
    facade: MessageCreatedFacade,
    dao: DAO,
) -> None:
    user_id: int = update.user_id  # pyright: ignore [reportAssignmentType]
    username: str = update.message.sender.username  # pyright: ignore [reportAttributeAccessIssue, reportAssignmentType]
    full_name: str = update.message.sender.full_name  # pyright: ignore [reportAttributeAccessIssue, reportAssignmentType]

    if not command.args:
        user = await dao.get_user_by_id(user_id=user_id)

        if not user:
            user = models.User(id=user_id, username=username, name=full_name)

            dao.add(instance=user)
            await dao.commit()

        await facade.send_message(text=texts.start.format(full_name=user.name))
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)

        return

    user = await dao.get_user_by_id(user_id=user_id)

    if not command.args.isdigit():
        await facade.send_message(text=texts.start.format(full_name=user.name))
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)

        return

    mini_test_id = int(command.args)

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test:
        await facade.send_message(text=texts.start.format(full_name=user.name))
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)

        return

    media = None

    if mini_test.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=mini_test.photo_file_id)),
        ]

    keyboard = keyboards.proceed_mini_test(mini_test_id=mini_test_id)

    if media:
        await facade.delete_message()
        await facade.answer(text=mini_test.title, media=media, keyboard=keyboard)

    else:
        await facade.answer_text(text=mini_test.title, keyboard=keyboard)
