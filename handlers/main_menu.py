import re

from maxo import types
from maxo.errors.api import MaxBotBadRequestError, MaxBotForbiddenError
from maxo.routing import filters, updates
from maxo.routing.facades import BotStartedFacade, MessageCallbackFacade, MessageCreatedFacade
from maxo.routing.routers.simple import Router

import keyboards
import texts
from database import DAO, models
from keyboards import callback_payload
from op_access import (
    OP_CHANNELS_PHASE1,
    OP_NOT_CONFIRMED_TEXT,
    block_callback_by_op_access,
    is_op_access_required,
    optional_step_is_waiting,
    pass_op_access_if_allowed,
    send_op_access_message,
)

MINI_TEST_PAYLOAD_REGEX = re.compile(r"mini\-(\d+)$")
QUIZ_PAYLOAD_REGEX = re.compile(r"quiz\-(\d+)$")
REF_PAYLOAD_REGEX = re.compile(r"^test2005$")
REF_SLUG = "test2005"

router = Router()


@router.bot_started()
async def handle_bot_start(update: updates.BotStarted, facade: BotStartedFacade, dao: DAO) -> None:  # noqa: C901, PLR0912
    user_id = update.user.user_id

    user = await dao.get_user_by_id(user_id=user_id)
    is_new_user = user is None

    if not user:
        user = models.User(id=user_id, username=update.user.username, name=update.user.full_name)

        dao.add(instance=user)
        await dao.commit()

    if type(update.payload) is str:
        if match := REF_PAYLOAD_REGEX.match(update.payload):
            if is_new_user:
                user.is_op_ref_user = True
                user.op_access_granted = False

            referral_stats = await dao.get_referral_stats_by_slug(slug=match.group(0))

            if not referral_stats:
                referral_stats = models.ReferralStats(
                    slug=match.group(0),
                    new_users_count=0,
                    old_users_count=0,
                )

            if is_new_user:
                referral_stats.new_users_count += 1
            else:
                referral_stats.old_users_count += 1

            dao.add(instance=referral_stats)
            dao.add(instance=user)
            await dao.commit()

        if match := MINI_TEST_PAYLOAD_REGEX.match(update.payload):
            mini_test_id = int(match.group(1))

            mini_test = await dao.get_mini_test_by_id(mini_test_id=mini_test_id)

            if mini_test:
                media = None

                if mini_test.photo_file_id:
                    media = [
                        types.PhotoAttachmentRequest(
                            payload=types.PhotoAttachmentRequestPayload(token=mini_test.photo_file_id),
                        ),
                    ]

                keyboard = keyboards.proceed_mini_test(mini_test_id=mini_test_id)
                try:
                    await facade.send_message(text=mini_test.title, media=media, keyboard=keyboard)
                except MaxBotForbiddenError:
                    return

                return

        elif match := QUIZ_PAYLOAD_REGEX.match(update.payload):
            quiz_id = int(match.group(1))

            quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

            if quiz:
                media = None

                if quiz.photo_file_id:
                    media = [
                        types.PhotoAttachmentRequest(
                            payload=types.PhotoAttachmentRequestPayload(token=quiz.photo_file_id),
                        ),
                    ]

                keyboard = keyboards.proceed_quiz(quiz_id=quiz_id)
                try:
                    await facade.send_message(text=quiz.title, media=media, keyboard=keyboard)
                except MaxBotForbiddenError:
                    return

                return

    try:
        await facade.send_message(text=texts.start.format(full_name=user.name))
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)
    except MaxBotForbiddenError:
        return


@router.message_callback(callback_payload.OpChannelsCheck.filter())
async def handle_op_channels_check(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    user = await dao.get_user_by_id(user_id=user_id)

    async def _safe_show_main_menu() -> None:
        try:
            await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)
        except MaxBotBadRequestError as error:
            if "error.edit.invalid.message" not in str(error):
                raise

            await facade.answer_text(text=texts.main_menu, keyboard=keyboards.main_menu)

    if not await is_op_access_required(user):
        await _safe_show_main_menu()
        return

    passed = await pass_op_access_if_allowed(user_id=user_id, dao=dao)

    if passed:
        await _safe_show_main_menu()
        return

    if optional_step_is_waiting(user_id=user_id):
        await send_op_access_message(user_id=user_id, facade=facade)
        return

    await send_op_access_message(
        user_id=user_id,
        facade=facade,
        warning_text=OP_NOT_CONFIRMED_TEXT,
    )


@router.message_callback(callback_payload.FriendshipTest.filter())
async def handle_friendship_test(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    if await block_callback_by_op_access(user_id=update.user.user_id, facade=facade, dao=dao):
        return

    await facade.answer_text(text=texts.main_menu)


@router.message_created(filters.Command("r"))
async def handle_ref_report(
    _: updates.MessageCreated,
    facade: MessageCreatedFacade,
    dao: DAO,
) -> None:
    ref_url = "https://max.ru/{bot_username}?start={slug}"
    bot_user = await facade.get_my_info()
    referral_stats = await dao.get_referral_stats_by_slug(slug=REF_SLUG)
    ref_url_value = ref_url.format(bot_username=bot_user.username, slug=REF_SLUG)

    if not bot_user.username:
        ref_url_value = f"https://max.ru/?start={REF_SLUG}"

    new_users_count = 0
    old_users_count = 0

    if referral_stats:
        new_users_count = referral_stats.new_users_count
        old_users_count = referral_stats.old_users_count
    passed_op_count = await dao.get_passed_op_users_count()
    links_text = "\n".join(
        f"{index}. {channel.display_link}"
        for index, channel in enumerate(OP_CHANNELS_PHASE1, start=1)
    )

    report = (
        f"{ref_url_value}\n"
        f"Новые юзеры: {new_users_count}\n"
        f"Старые: {old_users_count}\n"
        f"Прошли Оп: {passed_op_count}\n"
        f"{links_text}"
    )

    await facade.send_message(text=report)


@router.message_created(filters.CommandStart())
async def handle_start_command(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    dao: DAO,
) -> None:
    user_id: int = update.user_id  # pyright: ignore [reportAssignmentType]
    username: str = update.message.sender.username  # pyright: ignore [reportAttributeAccessIssue, reportAssignmentType]
    full_name: str = update.message.sender.full_name  # pyright: ignore [reportAttributeAccessIssue, reportAssignmentType]

    user = await dao.get_user_by_id(user_id=user_id)

    if not user:
        user = models.User(id=user_id, username=username, name=full_name)

        dao.add(instance=user)
        await dao.commit()

    try:
        await facade.send_message(text=texts.start.format(full_name=user.name))
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)
    except MaxBotForbiddenError:
        return


@router.message_created(filters.Command("reset1234"))
async def handle_reset_user_data(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    dao: DAO,
) -> None:
    user_id: int = update.user_id  # pyright: ignore [reportAssignmentType]
    user = await dao.get_user_by_id(user_id=user_id)

    if user:
        referral_stats = await dao.get_referral_stats_by_slug(slug=REF_SLUG)
        if referral_stats:
            if user.is_op_ref_user and referral_stats.new_users_count > 0:
                referral_stats.new_users_count -= 1
            elif referral_stats.old_users_count > 0:
                referral_stats.old_users_count -= 1

            dao.add(instance=referral_stats)

        mini_tests = await dao.get_mini_tests_by_user_id(user_id=user_id)
        quizzes = await dao.get_quizzes_by_user_id(user_id=user_id)

        for mini_test in mini_tests:
            await dao.delete(instance=mini_test)

        for quiz in quizzes:
            await dao.delete(instance=quiz)

        await dao.delete(instance=user)
        await dao.commit()

    await facade.send_message(text="удалил")

