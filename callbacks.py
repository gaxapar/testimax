from maxo.routing.filters.payload import Payload


class Cancel(Payload, prefix="cancel"):
    pass


class MiniTestsList(Payload, prefix="mini_tests_list"):
    page: int


class FriendshipTest(Payload, prefix="friendship_test"):
    pass


class MyMiniTests(Payload, prefix="my_mini_tests"):
    pass


class CreateMiniTest(Payload, prefix="create_mini_test"):
    pass


class RandomMiniTest(Payload, prefix="random_mini_test"):
    pass


class InteractiveTestsList(Payload, prefix="interactive_tests_list"):
    page: int


class OpenInteractiveTest(Payload, prefix="open_interactive_test"):
    slug: str


class ProceedInteractiveTest(Payload, prefix="proceed_interactive_test"):
    slug: str


class InteractiveTestOption(Payload, prefix="interactive_test_option"):
    slug: str
    question_index: int
    option_index: int


class SaveMiniTest(Payload, prefix="save_mini_test"):
    pass


class MiniTestDetails(Payload, prefix="mini_test_details"):
    mini_test_id: int


class AddMiniTestPhoto(Payload, prefix="add_mini_test_photo"):
    mini_test_id: int


class MiniTestAnswers(Payload, prefix="mini_test_answers"):
    mini_test_id: int


class DeleteMiniTest(Payload, prefix="delete_mini_test"):
    mini_test_id: int


class DeleteMiniTestConfirm(Payload, prefix="delete_mini_test_confirm"):
    mini_test_id: int


class AddMiniTestAnswer(Payload, prefix="add_mini_test_answer"):
    mini_test_id: int


class RemoveMiniTestAnswerList(Payload, prefix="remove_mini_test_answer_list"):
    mini_test_id: int


class RemoveMiniTestAnswer(Payload, prefix="remove_mini_test_answer"):
    mini_test_id: int
    answer_id: int


class OpenMiniTestToProceed(Payload, prefix="open_mini_test_to_proceed"):
    mini_test_id: int


class ProceedMiniTest(Payload, prefix="proceed_mini_test"):
    mini_test_id: int


class BackToMiniTestDetails(Payload, prefix="back_to_mini_test_details"):
    mini_test_id: int


class BackToMyMiniTests(Payload, prefix="back_to_my_mini_tests"):
    pass


class BackToMainMenu(Payload, prefix="back_to_main_menu"):
    pass


class Empty(Payload, prefix="empty"):
    pass
