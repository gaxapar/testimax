import urllib.parse
from collections.abc import Sequence

from maxo import types

import texts
from database import models
from database.models import Quiz
from utils import QuizAnswerDict

from . import callback_payload
from .main import PAGE_SIZE

save_quiz = [[types.CallbackButton(text=texts.save_quiz_button, payload=callback_payload.SaveQuiz().pack())]]
save_quiz_answers = [
    [types.CallbackButton(text=texts.save_quiz_answers_button, payload=callback_payload.ContinueQuizAnswers().pack())],
]


def my_quizzes_keyboard(quizzes: Sequence[Quiz]) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=quiz.title,
                payload=callback_payload.QuizDetails(quiz_id=quiz.id).pack(),
            ),
        ]
        for quiz in quizzes
    ]

    keyboard.extend(
        [
            [
                types.CallbackButton(
                    text=texts.create_quiz_button,
                    payload=callback_payload.CreateQuiz().pack(),
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


def quiz_menu(quiz: Quiz, bot_username: str) -> list[list[types.CallbackButton | types.LinkButton]]:
    text_to_share = texts.test_share_text.format(bot_username=bot_username, test_id=quiz.id, title=quiz.title)

    return [
        [
            types.LinkButton(
                text=texts.share_quiz_button,
                url=f"https://max.ru/:share?text={urllib.parse.quote(text_to_share)}",
            ),
        ],
        [
            types.CallbackButton(
                text=texts.add_quiz_photo_button,
                payload=callback_payload.AddQuizPhoto(quiz_id=quiz.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.quiz_questions_button,
                payload=callback_payload.QuizQuestions(quiz_id=quiz.id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.delete_quiz_button,
                payload=callback_payload.DeleteQuiz(quiz_id=quiz.id).pack(),
            ),
        ],
        [types.CallbackButton(text=texts.back, payload=callback_payload.BackToMyQuizzes().pack())],
    ]


def delete_quiz_confirm(quiz_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.delete_quiz_confirm_button,
                payload=callback_payload.DeleteQuizConfirm(quiz_id=quiz_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToQuizDetails(quiz_id=quiz_id).pack(),
            ),
        ],
    ]


def quiz_questions_menu(quiz_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.add_quiz_question_button,
                payload=callback_payload.AddQuizQuestion(quiz_id=quiz_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToQuizDetails(quiz_id=quiz_id).pack(),
            ),
        ],
    ]


def proceed_quiz(quiz_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.proceed_quiz_button,
                payload=callback_payload.ProceedQuiz(quiz_id=quiz_id).pack(),
            ),
        ],
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToMainMenu().pack(),
            ),
        ],
    ]


def select_correct_answer_menu(answers: Sequence[QuizAnswerDict]) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=answer["text"][:40],
                payload=callback_payload.AddQuizAnswer(answer_index=i).pack(),
            ),
        ]
        for i, answer in enumerate(answers)
    ]


def proceed_quiz_answers_keyboard(answers: Sequence[models.QuizAnswer]) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=answer.text,
                payload=callback_payload.QuizAnswer(answer_id=answer.id).pack(),
            ),
        ]
        for answer in answers
    ]


def quizzes_page(quizzes: Sequence[Quiz], page: int, pages_count: int) -> list[list[types.CallbackButton]]:
    keyboard = [
        [
            types.CallbackButton(
                text=f"{(page - 1) * PAGE_SIZE + num}. {quiz.title}",
                payload=callback_payload.OpenQuizToProceed(quiz_id=quiz.id).pack(),
            ),
        ]
        for num, quiz in enumerate(quizzes, start=1)
    ]

    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(
            types.CallbackButton(
                text=texts.previous_page_button,
                payload=callback_payload.QuizzesList(page=page - 1).pack(),
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
                payload=callback_payload.QuizzesList(page=page + 1).pack(),
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


def back_to_quiz(quiz_id: int) -> list[list[types.CallbackButton]]:
    return [
        [
            types.CallbackButton(
                text=texts.back,
                payload=callback_payload.BackToQuizDetails(quiz_id=quiz_id).pack(),
            ),
        ],
    ]
