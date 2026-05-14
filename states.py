from maxo.fsm import State, StatesGroup


class CreateMiniTest(StatesGroup):
    waiting_for_title = State()
    waiting_for_answers = State()


class AddMiniTestAnswer(StatesGroup):
    waiting_for_answers = State()


class AddMiniTestPhoto(StatesGroup):
    waiting_for_photo = State()
