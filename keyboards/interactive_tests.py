from collections.abc import Sequence

import callback_payload
from maxo import types

import texts
from utils import InteractiveTest

from .main import PAGE_SIZE


def interactive_tests_page(
    interactive_tests: Sequence[InteractiveTest],
    page: int,
    pages_count: int,
) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=f"{(page - 1) * PAGE_SIZE + num}. {interactive_test.title}",
                payload=callback_payload.OpenInteractiveTest(slug=interactive_test.slug).pack(),
            ),
        ]
        for num, interactive_test in enumerate(interactive_tests, start=1)
    ]

    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.previous_page_button,
                payload=callback_payload.InteractiveTestsList(page=page - 1).pack(),
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
                payload=callback_payload.InteractiveTestsList(page=page + 1).pack(),
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


def interactive_test_menu(interactive_test: InteractiveTest) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.proceed_interactive_test_button,
                payload=callback_payload.ProceedInteractiveTest(slug=interactive_test.slug).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.InteractiveTestsList(page=1).pack(),
            ),
        ],
    ]


def proceed_interactive_test_menu(
    interactive_test: InteractiveTest,
    question_index: int,
) -> list[list[types.CallbackButton]]:
    question = interactive_test.questions[question_index]

    return [
        [
            types.CallbackButton(
                text=option.text,
                payload=callback_payload.InteractiveTestOption(
                    slug=interactive_test.slug,
                    question_index=question_index,
                    option_index=i,
                ).pack(),
            ),
        ]
        for i, option in enumerate(question.options)
    ]
