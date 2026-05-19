import urllib.parse
from collections.abc import Sequence

from maxo import types

import texts
from database.models import MiniTest, MiniTestAnswer

from . import callback_payload
from .main import PAGE_SIZE


def my_mini_tests_keyboard(mini_tests: Sequence[MiniTest]) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=mini_test.title,
                payload=callback_payload.MiniTestDetails(mini_test_id=mini_test.id).pack(),
            ),
        ]
        for mini_test in mini_tests
    ]

    keyboard.extend(
        [
            [
                types.CallbackButton(
                    text=texts.create_mini_test_button,
                    payload=callback_payload.CreateMiniTest().pack(),
                ),
            ],
            [
                types.CallbackButton(
                    text=texts.back,
                    payload=callback_payload.BackToMainMenu().pack(),
                ),
            ],
        ],
    )

    return keyboard


def mini_test_menu(mini_test: MiniTest, bot_username: str) -> list[list[types.CallbackButton | types.LinkButton]]:
    text_to_share = texts.mini_test_share_text.format(
        bot_username=bot_username,
        test_id=mini_test.id,
        title=mini_test.title,
    )

    return [
        [
            types.LinkButton(
                text=texts.share_mini_test_button,
                url=f"https://max.ru/:share?text={urllib.parse.quote(text_to_share)}",
            ),
        ],
        [
            types.CallbackButton(
                text=texts.add_mini_test_photo_button,
                payload=callback_payload.AddMiniTestPhoto(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.mini_test_answers_button,
                payload=callback_payload.MiniTestAnswers(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.delete_mini_test_button,
                payload=callback_payload.DeleteMiniTest(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [types.CallbackButton(text=texts.back, payload=callback_payload.BackToMyMiniTests().pack())],
    ]


def delete_mini_test_confirm(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.delete_mini_test_confirm_button,
                payload=callback_payload.DeleteMiniTestConfirm(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    ]


def mini_test_answers_menu(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.add_mini_test_answer_button,
                payload=callback_payload.AddMiniTestAnswer(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.remove_mini_test_answer_button,
                payload=callback_payload.RemoveMiniTestAnswerList(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    ]


def remove_mini_test_answer_menu(
    mini_test_id: int,
    answers: Sequence[MiniTestAnswer],
) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=answer.text,
                payload=callback_payload.RemoveMiniTestAnswer(mini_test_id=mini_test_id, answer_id=answer.id).pack(),
            ),
        ]
        for answer in answers
    ]

    keyboard.append(
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    )

    return keyboard


def proceed_mini_test(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.proceed_mini_test_button,
                payload=callback_payload.ProceedMiniTest(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMainMenu().pack(),
            ),
        ],
    ]


def mini_tests_page(mini_tests: Sequence[MiniTest], page: int, pages_count: int) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=f"{(page - 1) * PAGE_SIZE + num}. {mini_test.title}",
                payload=callback_payload.OpenMiniTestToProceed(mini_test_id=mini_test.id).pack(),
            ),
        ]
        for num, mini_test in enumerate(mini_tests, start=1)
    ]

    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.previous_page_button,
                payload=callback_payload.MiniTestsList(page=page - 1).pack(),
            ),
        )

    else:
        navigation_buttons.append(
            types.CallbackButton(
                text="-",
                payload=callback_payload.Empty().pack(),
            ),
        )

    navigation_buttons.append(
        types.CallbackButton(
            text=f"{page}/{pages_count}",
            payload=callback_payload.Empty().pack(),
        ),
    )

    if page < pages_count:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.next_page_button,
                payload=callback_payload.MiniTestsList(page=page + 1).pack(),
            ),
        )

    else:
        navigation_buttons.append(
            types.CallbackButton(
                text="-",
                payload=callback_payload.Empty().pack(),
            ),
        )

    keyboard.append(navigation_buttons)

    keyboard.append(
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMainMenu().pack(),
            ),
        ],
    )

    return keyboard


def back_to_mini_test(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    ]
