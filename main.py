import asyncio
import json
import random
from pathlib import Path
from typing import Any

from maxo import Bot, types
from maxo.bot.defaults import BotDefaults
from maxo.enums import TextFormat
from maxo.fsm.context import FSMContext
from maxo.routing import filters, updates
from maxo.routing.dispatcher import Dispatcher
from maxo.routing.facades import BotStartedFacade, MessageCallbackFacade, MessageCreatedFacade
from maxo.routing.filters.command import CommandObject
from maxo.routing.routers.simple import Router
from maxo.transport.long_polling import LongPolling
from redis.asyncio import Redis

import callbacks
import keyboards
import states
import texts
from config import config
from database import DAO, DatabaseManager, models
from middlewares import DatabaseMiddleware
from utils import MiniTestAnswer

router = Router()

here = Path(__file__).parent

with Path.open(here / "channels.json") as file:
    channels: list[dict[str, Any]] = json.load(file)


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
                types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=mini_test.photo_file_id)),
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


@router.message_callback(callbacks.MiniTestsList.filter())
async def handle_mini_tests_list(
    _: updates.MessageCallback,
    payload: callbacks.MiniTestsList,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    page = payload.page

    mini_tests = await dao.get_mini_tests_page(page=page)
    pages_count = await dao.get_mini_tests_pages_count()

    if not mini_tests:
        await facade.answer_text(text=texts.no_tests_available)

        return

    keyboard = keyboards.mini_tests_page(mini_tests=mini_tests, page=page, pages_count=pages_count)
    await facade.edit_message(text=texts.mini_tests_list_menu, keyboard=keyboard)


@router.message_callback(callbacks.BackToMyMiniTests.filter())
@router.message_callback(callbacks.MyMiniTests.filter())
async def handle_my_mini_tests(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
    state: FSMContext,
) -> None:
    user_id = update.user.user_id

    mini_tests = await dao.get_mini_tests_by_user_id(user_id=user_id)

    if not mini_tests:
        await state.set_state(states.CreateMiniTest.waiting_for_title)
        await facade.edit_message(text=texts.enter_test_title, keyboard=keyboards.cancel)

        return

    keyboard = keyboards.my_mini_tests_keyboard(mini_tests=mini_tests)
    await facade.edit_message(text=texts.my_tests_list.format(user_tests_count=len(mini_tests)), keyboard=keyboard)


@router.message_callback(callbacks.CreateMiniTest.filter())
async def handle_create_mini_test(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.set_state(states.CreateMiniTest.waiting_for_title)
    await facade.edit_message(text=texts.enter_test_title, keyboard=keyboards.cancel)


@router.message_callback(callbacks.Cancel.filter())
async def handle_cancel(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)


@router.message_created(filters.StateFilter(states.CreateMiniTest.waiting_for_title))
async def handle_enter_test_title(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text:
        await facade.answer_text(text=texts.enter_test_title)

        return

    await state.update_data(title=update.text)
    await state.set_state(states.CreateMiniTest.waiting_for_answers)

    await facade.answer_text(text=texts.enter_test_answers, keyboard=keyboards.cancel)


@router.message_created(filters.StateFilter(states.AddMiniTestAnswer.waiting_for_answers))
@router.message_created(filters.StateFilter(states.CreateMiniTest.waiting_for_answers))
async def handle_enter_test_answers(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text:
        await facade.answer_text(text=texts.enter_test_answers_invalid)

        return

    data = await state.get_data()
    answers = data.get("answers", [])

    if update.message.body.photo:
        photo = update.message.body.photo[-1]
        answers.append(
            MiniTestAnswer(
                text=update.text or "",
                photo_file_id=photo.payload.token,
            ),
        )
    else:
        answers.append(MiniTestAnswer(text=update.text, photo_file_id=None))

    await state.update_data(answers=answers)

    await facade.answer_text(text=texts.enter_more_answers, keyboard=keyboards.save_mini_test)


@router.message_callback(callbacks.SaveMiniTest.filter())
async def handle_save_mini_test(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
    bot: Bot,
) -> None:
    user_id = update.user.user_id

    data = await state.get_data()
    answers: list[MiniTestAnswer] = data["answers"]
    mini_test_id: int | None = data.get("mini_test_id")

    user_id: int = update.user.user_id

    if mini_test_id:
        mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

        if not mini_test or mini_test.creator_user_id != user_id:
            await facade.answer_text(text=texts.mini_test_not_found)
            return

    else:
        title: str = data["title"]

        mini_test = models.MiniTest(title=title, creator_user_id=user_id)
        dao.add(instance=mini_test)

        await dao.commit()

    for answer_data in answers:
        answer = models.MiniTestAnswer(
            text=answer_data["text"],
            photo_file_id=answer_data["photo_file_id"],
            mini_test_id=mini_test.id,
        )
        dao.add(instance=answer)

    await dao.commit()

    await state.clear()

    place_in_top = await dao.get_mini_test_place_in_top(mini_test_id=mini_test.id)

    bot_user = await bot.get_my_info()

    if not bot_user.username:
        return

    text = texts.test_menu.format(title=mini_test.title, usages=mini_test.usages, place_in_top=place_in_top)
    keyboard = keyboards.mini_test_menu(mini_test=mini_test, bot_username=bot_user.username)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.MiniTestDetails.filter())
@router.message_callback(callbacks.BackToMiniTestDetails.filter())
async def handle_mini_test_details(
    update: updates.MessageCallback,
    payload: callbacks.MiniTestDetails | callbacks.BackToMiniTestDetails,
    facade: MessageCallbackFacade,
    dao: DAO,
    bot: Bot,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    place_in_top = await dao.get_mini_test_place_in_top(mini_test_id=mini_test.id)

    bot_user = await bot.get_my_info()

    if not bot_user.username:
        return

    text = texts.test_menu.format(title=mini_test.title, usages=mini_test.usages, place_in_top=place_in_top)
    keyboard = keyboards.mini_test_menu(mini_test=mini_test, bot_username=bot_user.username)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.DeleteMiniTest.filter())
async def handle_delete_mini_test(
    update: updates.MessageCallback,
    payload: callbacks.DeleteMiniTest,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    text = texts.delete_mini_test_confirm.format(title=mini_test.title)
    keyboard = keyboards.delete_mini_test_confirm(mini_test_id=mini_test_id)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.DeleteMiniTestConfirm.filter())
async def handle_delete_mini_test_confirm(
    update: updates.MessageCallback,
    payload: callbacks.DeleteMiniTestConfirm,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    await dao.delete(instance=mini_test)
    await dao.commit()

    mini_tests = await dao.get_mini_tests_by_user_id(user_id=user_id)

    keyboard = keyboards.my_mini_tests_keyboard(mini_tests=mini_tests)
    await facade.edit_message(text=texts.my_tests_list.format(user_tests_count=len(mini_tests)), keyboard=keyboard)


@router.message_callback(callbacks.AddMiniTestPhoto.filter())
async def handle_add_mini_test_photo(
    update: updates.MessageCallback,
    payload: callbacks.AddMiniTestPhoto,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    await state.update_data(mini_test_id=mini_test_id)
    await state.set_state(states.AddMiniTestPhoto.waiting_for_photo)

    await facade.edit_message(
        text=texts.send_mini_test_photo,
        keyboard=keyboards.back_to_mini_test(mini_test_id=mini_test_id),
    )


@router.message_created(filters.StateFilter(states.AddMiniTestPhoto.waiting_for_photo))
async def handle_save_mini_test_photo(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    if not update.message.body.photo:
        await facade.answer_text(text=texts.send_mini_test_photo_invalid)

        return

    photo = update.message.body.photo[-1]

    data = await state.get_data()
    mini_test_id = data["mini_test_id"]

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    mini_test.photo_file_id = photo.payload.token
    dao.add(instance=mini_test)
    await dao.commit()

    place_in_top = await dao.get_mini_test_place_in_top(mini_test_id=mini_test.id)

    bot_user = await facade.get_my_info()

    if not bot_user.username:
        return

    text = texts.test_menu.format(title=mini_test.title, usages=mini_test.usages, place_in_top=place_in_top)
    keyboard = keyboards.mini_test_menu(mini_test=mini_test, bot_username=bot_user.username)

    await facade.answer_text(text=text, keyboard=keyboard)


@router.message_callback(callbacks.MiniTestAnswers.filter())
async def handle_mini_test_answers(
    update: updates.MessageCallback,
    payload: callbacks.MiniTestAnswers,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    answers = await dao.get_answers_by_mini_test_id(mini_test_id=mini_test_id)

    text = texts.mini_test_answers_menu.format(answers=", ".join(answer.text for answer in answers))
    keyboard = keyboards.mini_test_answers_menu(mini_test_id=mini_test_id)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.AddMiniTestAnswer.filter())
async def handle_add_mini_test_answer(
    update: updates.MessageCallback,
    payload: callbacks.AddMiniTestAnswer,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    await state.update_data(mini_test_id=mini_test_id)
    await state.set_state(states.AddMiniTestAnswer.waiting_for_answers)

    await facade.edit_message(text=texts.enter_test_answers, keyboard=keyboards.cancel)


@router.message_callback(callbacks.RemoveMiniTestAnswerList.filter())
async def handle_remove_mini_test_answer_list(
    update: updates.MessageCallback,
    payload: callbacks.RemoveMiniTestAnswerList,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    answers = await dao.get_answers_by_mini_test_id(mini_test_id=mini_test_id)

    text = texts.remove_mini_test_answer_menu
    keyboard = keyboards.remove_mini_test_answer_menu(mini_test_id=mini_test_id, answers=answers)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.RemoveMiniTestAnswer.filter())
async def handle_remove_mini_test_answer(
    update: updates.MessageCallback,
    payload: callbacks.RemoveMiniTestAnswer,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id
    answer_id = payload.answer_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test or mini_test.creator_user_id != user_id:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    answer = await dao.get_mini_test_answer_by_id(mini_test_answer_id=answer_id)

    if not answer or answer.mini_test_id != mini_test_id:
        await facade.answer_text(text=texts.mini_test_answer_not_found)
        return

    await dao.delete(instance=answer)
    await dao.commit()

    answers = await dao.get_answers_by_mini_test_id(mini_test_id=mini_test_id)

    text = texts.mini_test_answers_menu.format(answers=", ".join(answer.text for answer in answers))
    keyboard = keyboards.mini_test_answers_menu(mini_test_id=mini_test_id)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callbacks.RandomMiniTest.filter())
async def handle_random_mini_test(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    mini_test = await dao.get_random_mini_test()

    if not mini_test:
        await facade.answer_text(text=texts.no_tests_available)

        return

    keyboard = keyboards.proceed_mini_test(mini_test_id=mini_test.id)

    await facade.edit_message(text=mini_test.title, keyboard=keyboard)


@router.message_callback(callbacks.OpenMiniTestToProceed.filter())
async def handle_open_mini_test_to_proceed(
    _: updates.MessageCallback,
    payload: callbacks.OpenMiniTestToProceed,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test:
        await facade.answer_text(text=texts.mini_test_not_found)
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
        await facade.edit_message(text=mini_test.title, keyboard=keyboard)


@router.message_callback(callbacks.ProceedMiniTest.filter())
async def handle_proceed_mini_test(
    update: updates.MessageCallback,
    payload: callbacks.ProceedMiniTest,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    mini_test_id = payload.mini_test_id

    mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

    if not mini_test:
        await facade.answer_text(text=texts.mini_test_not_found)
        return

    answers = await dao.get_answers_by_mini_test_id(mini_test_id=mini_test_id)

    if not answers:
        await facade.answer_text(texts.no_answers_available)
        return

    if mini_test.creator_user_id != user_id:
        mini_test.usages += 1

        await dao.commit()

    answer = random.choice(answers)  # noqa: S311

    media = None

    if answer.photo_file_id:
        media = [types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=answer.photo_file_id))]

    await facade.delete_message()
    await facade.answer(text=answer.text, media=media)

    await facade.answer_text(text=texts.main_menu, keyboard=keyboards.main_menu)


@router.message_callback(callbacks.BackToMainMenu.filter())
async def handle_back_to_main_menu(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)


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
    dispatcher.include_router(router=router)

    dispatcher.bot_started.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]
    dispatcher.message_created.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]
    dispatcher.message_callback.outer_middleware(DatabaseMiddleware(database_manager=database_manager))  # pyright: ignore[reportArgumentType]

    await LongPolling(dispatcher=dispatcher).start(bot=bot, drop_pending_updates=True)


asyncio.run(main())
