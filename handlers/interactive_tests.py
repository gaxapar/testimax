import json
from pathlib import Path
from typing import Any

from maxo import types
from maxo.fsm.context import FSMContext
from maxo.routing import updates
from maxo.routing.facades import MessageCallbackFacade
from maxo.routing.routers.simple import Router

import keyboards
import texts
import utils
from database import DAO
from keyboards import callback_payload
from op_access import block_callback_by_op_access

router = Router()

here = Path(__file__).parent.parent
interactive_tests_folder = here / "interactive_tests"

with Path.open(here / "channels.json") as file:
    channels: list[dict[str, Any]] = json.load(file)

INTERACTIVE_TESTS_PAGE_SIZE = 8

interactive_tests: dict[str, utils.InteractiveTest] = {}

for test_file in interactive_tests_folder.glob("*.yaml"):
    interactive_test = utils.load_interactive_test(path=test_file)
    interactive_tests[interactive_test.slug] = interactive_test

INTERACTIVE_TESTS_PAGES_COUNT = (len(interactive_tests) + INTERACTIVE_TESTS_PAGE_SIZE - 1) // INTERACTIVE_TESTS_PAGE_SIZE  # noqa: E501 # fmt: skip


@router.message_callback(callback_payload.InteractiveTestsList.filter())
async def handle_interactive_tests_list(
    update: updates.MessageCallback,
    payload: callback_payload.InteractiveTestsList,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    if await block_callback_by_op_access(user_id=update.user.user_id, facade=facade, dao=dao):
        return

    keyboard = keyboards.interactive_tests_page(
        interactive_tests=list(interactive_tests.values()),
        page=payload.page,
        pages_count=INTERACTIVE_TESTS_PAGES_COUNT,
    )
    await facade.edit_message(text=texts.interactive_tests_list_menu, keyboard=keyboard)


@router.message_callback(callback_payload.OpenInteractiveTest.filter())
async def handle_open_interactive_test(
    _: updates.MessageCallback,
    payload: callback_payload.OpenInteractiveTest,
    facade: MessageCallbackFacade,
) -> None:
    interactive_test = interactive_tests.get(payload.slug)

    if not interactive_test:
        await facade.answer_text(text=texts.interactive_test_not_found)
        return

    media = [
        types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=interactive_test.photo)),
    ]

    keyboard = keyboards.interactive_test_menu(interactive_test=interactive_test)

    await facade.delete_message()
    await facade.answer(text=interactive_test.description, media=media, keyboard=keyboard)


@router.message_callback(callback_payload.ProceedInteractiveTest.filter())
async def handle_proceed_interactive_test(
    _: updates.MessageCallback,
    payload: callback_payload.ProceedInteractiveTest,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    interactive_test = interactive_tests.get(payload.slug)

    if not interactive_test:
        await facade.answer_text(text=texts.interactive_test_not_found)
        return

    for result in interactive_test.results:
        await state.update_data({result.slug: 0})

    question = interactive_test.questions[0]

    media = [
        types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=question.photo)),
    ]

    text = texts.interactive_test_question_wrapper.format(
        test_title=interactive_test.title,
        question_number=1,
        total_questions=len(interactive_test.questions),
        question=question.question,
    )
    keyboard = keyboards.proceed_interactive_test_menu(interactive_test=interactive_test, question_index=0)

    await facade.edit_message(text=text, media=media, keyboard=keyboard)


@router.message_callback(callback_payload.InteractiveTestOption.filter())
async def handle_interactive_test_question_answer(
    _: updates.MessageCallback,
    payload: callback_payload.InteractiveTestOption,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    interactive_test = interactive_tests.get(payload.slug)

    if not interactive_test:
        await facade.answer_text(text=texts.interactive_test_not_found)
        return

    question_index = payload.question_index
    option_index = payload.option_index

    question = interactive_test.questions[question_index]
    option = question.options[option_index]

    data = await state.get_data()

    for result_slug, points in option.points.items():
        current_points = data.get(result_slug, 0)
        await state.update_data({result_slug: current_points + points})

    if question_index == len(interactive_test.questions) - 1:
        data = await state.get_data()
        best_result = max(interactive_test.results, key=lambda r: data.get(r.slug, 0))

        await state.clear()

        await facade.edit_message(text=best_result.description)
        await facade.send_message(text=texts.main_menu, keyboard=keyboards.main_menu)

        return

    question_index += 1
    next_question = interactive_test.questions[question_index]

    text = texts.interactive_test_question_wrapper.format(
        test_title=interactive_test.title,
        question_number=question_index + 1,
        total_questions=len(interactive_test.questions),
        question=next_question.question,
    )
    keyboard = keyboards.proceed_interactive_test_menu(interactive_test=interactive_test, question_index=question_index)

    media = [
        types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=next_question.photo)),
    ]

    await facade.edit_message(text=text, media=media, keyboard=keyboard)
