from maxo import types

import texts

from . import callback_payload

PAGE_SIZE = 10

main_menu = [
    [
        types.CallbackButton(text=texts.mini_tests_list_button, payload=callback_payload.MiniTestsList(page=1).pack()),
        types.CallbackButton(text=texts.quizzes_list_button, payload=callback_payload.QuizzesList(page=1).pack()),
    ],
    [
        types.CallbackButton(text=texts.friendship_test_button, payload=callback_payload.FriendshipTest().pack()),
    ],
    [
        types.CallbackButton(text=texts.my_mini_tests_button, payload=callback_payload.MyMiniTests().pack()),
        types.CallbackButton(text=texts.random_mini_test_button, payload=callback_payload.RandomMiniTest().pack()),
    ],
    [
        types.CallbackButton(text=texts.my_quizzes_button, payload=callback_payload.MyQuizzes().pack()),
        types.CallbackButton(text=texts.random_quiz_button, payload=callback_payload.RandomQuiz().pack()),
    ],
    [
        types.CallbackButton(
            text=texts.interactive_tests_button,
            payload=callback_payload.InteractiveTestsList(page=1).pack(),
        ),
    ],
]

cancel = [[types.CallbackButton(text=texts.cancel, payload=callback_payload.Cancel().pack())]]

save_mini_test = [
    [types.CallbackButton(text=texts.save_mini_test_button, payload=callback_payload.SaveMiniTest().pack())],
]
