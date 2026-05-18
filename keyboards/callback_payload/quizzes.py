from maxo.routing.filters.payload import Payload


class QuizzesList(Payload, prefix="quizzes_list"):
    page: int


class MyQuizzes(Payload, prefix="my_quizzes"):
    pass


class CreateQuiz(Payload, prefix="create_quiz"):
    pass


class RandomQuiz(Payload, prefix="random_quiz"):
    pass


class SaveQuiz(Payload, prefix="save_quiz"):
    pass


class QuizDetails(Payload, prefix="quiz_details"):
    quiz_id: int


class AddQuizPhoto(Payload, prefix="add_quiz_photo"):
    quiz_id: int


class QuizQuestions(Payload, prefix="quiz_questions"):
    quiz_id: int


class EditQuizQuestion(Payload, prefix="edit_quiz_question"):
    question_id: int


class DeleteQuizQuestion(Payload, prefix="delete_quiz_question"):
    question_id: int


class EditQuizAnswer(Payload, prefix="edit_quiz_answer"):
    answer_id: int


class DeleteQuizAnswer(Payload, prefix="delete_quiz_answer"):
    answer_id: int


class AddQuizQuestion(Payload, prefix="add_quiz_question"):
    quiz_id: int | None = None


class AddQuizAnswer(Payload, prefix="add_quiz_answer"):
    answer_index: int


class ContinueQuizAnswers(Payload, prefix="continue_quiz_answers"):
    pass


class DeleteQuiz(Payload, prefix="delete_quiz"):
    quiz_id: int


class DeleteQuizConfirm(Payload, prefix="delete_quiz_confirm"):
    quiz_id: int


class OpenQuizToProceed(Payload, prefix="open_quiz_to_proceed"):
    quiz_id: int


class ProceedQuiz(Payload, prefix="proceed_quiz"):
    quiz_id: int


class BackToQuizDetails(Payload, prefix="back_to_quiz_details"):
    quiz_id: int


class BackToMyQuizzes(Payload, prefix="back_to_my_quizzes"):
    pass


class QuizAnswer(Payload, prefix="quiz_answer"):
    answer_id: int
