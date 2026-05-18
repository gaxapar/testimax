from maxo.fsm import State, StatesGroup


class CreateMiniTest(StatesGroup):
    waiting_for_title = State()
    waiting_for_answers = State()


class AddMiniTestAnswer(StatesGroup):
    waiting_for_answers = State()


class AddMiniTestPhoto(StatesGroup):
    waiting_for_photo = State()


class GetPhotoFileId(StatesGroup):
    waiting_for_photo = State()


class CreateQuiz(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_questions = State()


class AddQuizQuestion(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_answers = State()
    waiting_for_correct_answer = State()


class AddQuizPhoto(StatesGroup):
    waiting_for_photo = State()


class ProceedQuiz(StatesGroup):
    answering_question = State()


class EditQuizAnswer(StatesGroup):
    waiting_for_text = State()
