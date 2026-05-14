import urllib.parse
from collections.abc import Sequence

from maxo import types

import callbacks
import texts
from database.models import MiniTest, MiniTestAnswer

PAGE_SIZE = 10

main_menu = [
    [
        types.CallbackButton(text=texts.mini_tests_list_button, payload=callbacks.MiniTestsList(page=1).pack()),
    ],
    [
        types.CallbackButton(text=texts.friendship_test_button, payload=callbacks.FriendshipTest().pack()),
    ],
    [
        types.CallbackButton(text=texts.my_mini_tests_button, payload=callbacks.MyMiniTests().pack()),
        types.CallbackButton(text=texts.random_mini_test_button, payload=callbacks.RandomMiniTest().pack()),
    ],
]

cancel = [[types.CallbackButton(text=texts.cancel, payload=callbacks.Cancel().pack())]]

save_mini_test = [[types.CallbackButton(text=texts.save_mini_test_button, payload=callbacks.SaveMiniTest().pack())]]

def my_mini_tests_keyboard(mini_tests: Sequence[MiniTest]) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=mini_test.title,
                payload=callbacks.MiniTestDetails(mini_test_id=mini_test.id).pack(),
            ),
        ]
        for mini_test in mini_tests
    ]

    keyboard.extend(
        [
            [
                types.CallbackButton(
                    text=texts.create_mini_test_button,
                    payload=callbacks.CreateMiniTest().pack(),
                ),
            ],
            [
                types.CallbackButton(
                    text=texts.back,
                    payload=callbacks.BackToMainMenu().pack(),
                ),
            ],
        ],
    )

    return keyboard


def mini_test_menu(mini_test: MiniTest, bot_username: str) -> list[list[types.CallbackButton | types.LinkButton]]:
    text_to_share = texts.test_share_text.format(bot_username=bot_username, test_id=mini_test.id, title=mini_test.title)

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
                payload=callbacks.AddMiniTestPhoto(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.mini_test_answers_button,
                payload=callbacks.MiniTestAnswers(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.delete_mini_test_button,
                payload=callbacks.DeleteMiniTest(mini_test_id=mini_test.id).pack(),
            ),
        ],
        [types.CallbackButton(text=texts.back, payload=callbacks.BackToMyMiniTests().pack())],
    ]


def delete_mini_test_confirm(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.delete_mini_test_confirm_button,
                payload=callbacks.DeleteMiniTestConfirm(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    ]


def mini_test_answers_menu(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.add_mini_test_answer_button,
                payload=callbacks.AddMiniTestAnswer(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.remove_mini_test_answer_button,
                payload=callbacks.RemoveMiniTestAnswerList(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
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
                payload=callbacks.RemoveMiniTestAnswer(mini_test_id=mini_test_id, answer_id=answer.id).pack(),
            ),
        ]
        for answer in answers
    ]

    keyboard.append(
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    )

    return keyboard


def proceed_mini_test(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.proceed_mini_test_button,
                payload=callbacks.ProceedMiniTest(mini_test_id=mini_test_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMainMenu().pack(),
            ),
        ],
    ]


def mini_tests_page(mini_tests: Sequence[MiniTest], page: int, pages_count: int) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=f"{page - 1 * PAGE_SIZE + num}. {mini_test.title}",
                payload=callbacks.OpenMiniTestToProceed(mini_test_id=mini_test.id).pack(),
            ),
        ]
        for num, mini_test in enumerate(mini_tests, start=1)
    ]

    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.previous_page_button,
                payload=callbacks.MiniTestsList(page=page - 1).pack(),
            ),
        )

    else:
        navigation_buttons.append(
            types.CallbackButton(
                text="-",
                payload=callbacks.Empty().pack(),
            ),
        )

    navigation_buttons.append(
        types.CallbackButton(
            text=f"{page}/{pages_count}",
            payload=callbacks.Empty().pack(),
        ),
    )

    if page < pages_count:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.next_page_button,
                payload=callbacks.MiniTestsList(page=page + 1).pack(),
            ),
        )

    else:
        navigation_buttons.append(
            types.CallbackButton(
                text="-",
                payload=callbacks.Empty().pack(),
            ),
        )

    keyboard.append(navigation_buttons)

    keyboard.append(
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMainMenu().pack(),
            ),
        ],
    )

    return keyboard


def back_to_mini_test(mini_test_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.back,
                payload=callbacks.BackToMiniTestDetails(mini_test_id=mini_test_id).pack(),
            ),
        ],
    ]
