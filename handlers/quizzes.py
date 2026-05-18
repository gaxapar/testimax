from collections.abc import Sequence
from typing import TYPE_CHECKING

from maxo import Bot, types
from maxo.fsm.context import FSMContext
from maxo.routing import filters, updates
from maxo.routing.facades import MessageCallbackFacade, MessageCreatedFacade
from maxo.routing.routers.simple import Router

import keyboards
import states
import texts
from database import DAO, models
from keyboards import callback_payload

if TYPE_CHECKING:
    from utils import QuizQuestionDict

router = Router()


def format_question_list(questions: Sequence[str]) -> str:
    if not questions:
        return ""

    return "\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1))


def format_answer_list(answers: Sequence[models.QuizAnswer]) -> str:
    if not answers:
        return "Ответов пока нет"

    return "\n".join(
        f"{index}. {'✅ ' if answer.is_correct else ''}{answer.text}" for index, answer in enumerate(answers, start=1)
    )


def build_quiz_question_editor_text(question: models.QuizQuestion, answers: Sequence[models.QuizAnswer]) -> str:
    return f"<b>Вопрос:</b> {question.text}\n\n<b>Ответы:</b>\n{format_answer_list(answers)}"


@router.message_callback(callback_payload.QuizzesList.filter())
async def handle_quizzes_list(
    _: updates.MessageCallback,
    payload: callback_payload.QuizzesList,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    page = payload.page

    quizzes = await dao.get_quizzes_page(page=page)
    pages_count = await dao.get_quizzes_pages_count()

    if not quizzes:
        await facade.answer_text(text=texts.no_quizzes_available)
        return

    keyboard = keyboards.quizzes_page(quizzes=quizzes, page=page, pages_count=pages_count)
    await facade.edit_message(text=texts.quizzes_list_menu, keyboard=keyboard)


@router.message_callback(callback_payload.BackToMyQuizzes.filter())
@router.message_callback(callback_payload.MyQuizzes.filter())
async def handle_my_quizzes(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
    state: FSMContext,
) -> None:
    user_id = update.user.user_id

    quizzes = await dao.get_quizzes_by_user_id(user_id=user_id)

    if not quizzes:
        await state.set_state(states.CreateQuiz.waiting_for_title)
        await facade.edit_message(text=texts.enter_quiz_title, keyboard=keyboards.cancel)
        return

    keyboard = keyboards.my_quizzes_keyboard(quizzes=quizzes)
    await facade.edit_message(text=texts.my_quizzes_list.format(user_quizzes_count=len(quizzes)), keyboard=keyboard)


@router.message_callback(callback_payload.CreateQuiz.filter())
async def handle_create_quiz(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.set_state(states.CreateQuiz.waiting_for_title)
    await facade.edit_message(text=texts.enter_quiz_title, keyboard=keyboards.cancel)


@router.message_created(filters.StateFilter(states.CreateQuiz.waiting_for_title))
async def handle_enter_quiz_title(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text:
        await facade.answer_text(text=texts.enter_quiz_title_invalid)
        return

    await state.update_data(title=update.text)
    await state.set_state(states.CreateQuiz.waiting_for_description)

    await facade.answer_text(text=texts.enter_quiz_description, keyboard=keyboards.cancel)


@router.message_created(filters.StateFilter(states.CreateQuiz.waiting_for_description))
async def handle_enter_quiz_description(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text:
        await facade.answer_text(text=texts.enter_quiz_description_invalid)
        return

    await state.update_data(description=update.text, questions=[])
    await state.set_state(states.CreateQuiz.waiting_for_questions)

    # show options to add question or save quiz
    keyboard = [
        [types.CallbackButton(text=texts.add_quiz_question_button, payload=callback_payload.AddQuizQuestion().pack())],
        [types.CallbackButton(text=texts.save_quiz_button, payload=callback_payload.SaveQuiz().pack())],
        [types.CallbackButton(text=texts.back, payload=callback_payload.BackToMainMenu().pack())],
    ]

    await facade.answer_text(text=texts.enter_quiz_question, keyboard=keyboard)


@router.message_callback(callback_payload.AddQuizQuestion.filter())
async def handle_add_quiz_question(
    _: updates.MessageCallback,
    payload: callback_payload.AddQuizQuestion,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    # payload.quiz_id may be provided when adding to existing quiz
    await state.update_data(editing_quiz_id=payload.quiz_id)
    await state.set_state(states.AddQuizQuestion.waiting_for_question_text)

    await facade.edit_message(text=texts.enter_quiz_question, keyboard=keyboards.cancel)


@router.message_created(filters.StateFilter(states.AddQuizQuestion.waiting_for_question_text))
async def handle_enter_quiz_question_text(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text and not update.message.body.photo:
        await facade.answer_text(texts.enter_quiz_question_invalid)
        return

    current_question: QuizQuestionDict = {"text": update.text or "", "photo_file_id": None, "answers": []}

    if update.message.body.photo:
        photo = update.message.body.photo[-1]
        current_question["photo_file_id"] = photo.payload.token

    await state.update_data(current_question=current_question)
    await state.set_state(states.AddQuizQuestion.waiting_for_answers)

    await facade.answer_text(text=texts.enter_quiz_answers, keyboard=keyboards.cancel)


@router.message_created(filters.StateFilter(states.AddQuizQuestion.waiting_for_answers))
async def handle_enter_quiz_answers(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    if not update.text:
        await facade.answer_text(texts.enter_quiz_answers_invalid)
        return

    data = await state.get_data()
    current_question = data.get("current_question")
    if current_question is None:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    text = update.text

    # store answers without marking correctness yet
    current_question["answers"].append({"text": text})

    await state.update_data(current_question=current_question)

    await facade.answer_text(text=texts.enter_more_quiz_answers, keyboard=keyboards.save_quiz_answers)


@router.message_created(filters.StateFilter(states.EditQuizAnswer.waiting_for_text))
async def handle_edit_quiz_answer_text(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    if not update.text:
        await facade.answer_text(texts.enter_quiz_answers_invalid)
        return

    data = await state.get_data() or {}
    answer_id = data.get("editing_answer_id")
    question_id = data.get("editing_question_id")

    if not answer_id or not question_id:
        await facade.answer_text(texts.quiz_question_not_found)
        await state.clear()
        return

    answer = await dao.get_answer_by_id(answer_id=answer_id)
    if not answer:
        await facade.answer_text(texts.no_answers_available)
        await state.clear()
        return

    answer.text = update.text
    dao.add(instance=answer)
    await dao.commit()

    # reopen editor for question
    question = await dao.get_question_by_id(question_id=question_id)
    if question is None:
        await facade.answer_text(texts.quiz_question_not_found)
        await state.clear()
        return

    answers = await dao.get_answers_by_question_id(question_id=question.id)

    keyboard = keyboards.quiz_question_editor_keyboard(
        question_id=question.id,
        quiz_id=question.quiz_id,
        answers=answers,
    )

    await facade.edit_message(
        text=build_quiz_question_editor_text(question=question, answers=answers),
        keyboard=keyboard,
    )
    await state.clear()


@router.message_created(filters.StateFilter(states.AddQuizAnswerToQuestion.waiting_for_text))
async def handle_add_quiz_answer_to_question_text(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    if not update.text:
        await facade.answer_text(texts.enter_quiz_answer_invalid)
        return

    data = await state.get_data() or {}
    question_id = data.get("adding_answer_question_id")

    if not question_id:
        await facade.answer_text(texts.quiz_question_not_found)
        await state.clear()
        return

    question = await dao.get_question_by_id(question_id=question_id)
    if not question:
        await facade.answer_text(texts.quiz_question_not_found)
        await state.clear()
        return

    existing_answers = await dao.get_answers_by_question_id(question_id=question.id)
    answer = models.QuizAnswer(
        text=update.text,
        question_id=question.id,
        is_correct=not existing_answers,
    )
    dao.add(instance=answer)
    await dao.commit()

    answers = await dao.get_answers_by_question_id(question_id=question.id)
    keyboard = keyboards.quiz_question_editor_keyboard(
        question_id=question.id,
        quiz_id=question.quiz_id,
        answers=answers,
    )

    await facade.edit_message(
        text=build_quiz_question_editor_text(question=question, answers=answers),
        keyboard=keyboard,
    )
    await state.clear()


@router.message_callback(callback_payload.SaveQuiz.filter())
async def handle_save_quiz(
    update: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
    bot: Bot,
) -> None:
    user_id = update.user.user_id
    data = await state.get_data() or {}

    # If the user tries to save while a question is still being edited,
    # keep the save behavior tied to the explicit "save answers" callback.
    current_question = data.get("current_question")
    if current_question:
        await facade.answer_text(texts.save_quiz_answers_required)
        return

    # otherwise, save whole quiz
    title: str = data["title"]
    description: str = data.get("description", "")
    questions = data.get("questions", [])

    if not title:
        await facade.answer_text(text=texts.enter_quiz_title_invalid)
        return

    if not questions:
        await facade.answer_text(texts.no_questions_available)
        return

    # create quiz
    quiz = models.Quiz(title=title, description=description, creator_user_id=user_id)
    dao.add(instance=quiz)
    await dao.commit()

    for q in questions:
        question = models.QuizQuestion(text=q.get("text"), photo_file_id=q.get("photo_file_id"), quiz_id=quiz.id)
        dao.add(instance=question)
        await dao.commit()

        for a in q.get("answers", []):
            answer = models.QuizAnswer(
                text=a.get("text"),
                question_id=question.id,
                is_correct=bool(a.get("is_correct")),
            )
            dao.add(instance=answer)

    await dao.commit()

    await state.clear()

    place_in_top = await dao.get_quiz_place_in_top(quiz_id=quiz.id)

    bot_user = await bot.get_my_info()

    if not bot_user.username:
        return

    text = texts.quiz_menu.format(title=quiz.title, usages=quiz.usages, place_in_top=place_in_top)
    keyboard = keyboards.quiz_menu(quiz=quiz, bot_username=bot_user.username)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callback_payload.QuizDetails.filter())
@router.message_callback(callback_payload.BackToQuizDetails.filter())
async def handle_quiz_details(
    update: updates.MessageCallback,
    payload: callback_payload.QuizDetails | callback_payload.BackToQuizDetails,
    facade: MessageCallbackFacade,
    dao: DAO,
    bot: Bot,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    place_in_top = await dao.get_quiz_place_in_top(quiz_id=quiz.id)

    bot_user = await bot.get_my_info()

    if not bot_user.username:
        return

    text = texts.quiz_menu.format(title=quiz.title, usages=quiz.usages, place_in_top=place_in_top)
    keyboard = keyboards.quiz_menu(quiz=quiz, bot_username=bot_user.username)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callback_payload.ContinueQuizAnswers.filter())
async def handle_continue_quiz_answers(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    data = await state.get_data() or {}
    current_question = data.get("current_question")

    if not current_question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    answers = current_question.get("answers", [])

    if not answers:
        await facade.answer_text(texts.no_answers_available)
        return

    await state.set_state(states.AddQuizQuestion.waiting_for_correct_answer)

    keyboard = keyboards.select_correct_answer_menu(answers=answers)
    await facade.edit_message(text=texts.choose_correct_answer, keyboard=keyboard)


@router.message_callback(callback_payload.AddQuizAnswer.filter())
async def handle_add_quiz_answer(
    _: updates.MessageCallback,
    payload: callback_payload.AddQuizAnswer,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    data = await state.get_data() or {}
    current_question = data.get("current_question")

    if not current_question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    answer_index = payload.answer_index

    answers = current_question.get("answers", [])

    if answer_index < 0 or answer_index >= len(answers):
        await facade.answer_text(texts.quiz_question_not_found)
        return

    # mark correct answer
    for i, a in enumerate(answers):
        a["is_correct"] = i == answer_index

    # append question to quiz questions
    questions = data.get("questions", [])
    editing_quiz_id = data.get("editing_quiz_id")

    if editing_quiz_id:
        quiz = await dao.get_quiz_by_id(quiz_id=editing_quiz_id)

        if not quiz:
            await facade.answer_text(texts.quiz_not_found)
            return

        question = models.QuizQuestion(
            text=current_question["text"],
            photo_file_id=current_question.get("photo_file_id"),
            quiz_id=quiz.id,
        )
        dao.add(instance=question)
        await dao.commit()

        for a in current_question.get("answers", []):
            answer = models.QuizAnswer(
                text=a.get("text"),
                question_id=question.id,
                is_correct=bool(a.get("is_correct")),
            )
            dao.add(instance=answer)

        await dao.commit()
        await state.clear()

        questions = await dao.get_questions_by_quiz_id(quiz_id=quiz.id)
        keyboard = keyboards.quiz_questions_menu_with_items(quiz_id=quiz.id, questions=questions)
        await facade.edit_message(
            text=texts.quiz_questions_menu.format(questions=format_question_list([q.text for q in questions])),
            keyboard=keyboard,
        )
        return

    questions.append(current_question)
    await state.update_data(questions=questions)
    await state.update_data(current_question=None)
    await state.set_state(states.CreateQuiz.waiting_for_questions)

    # show menu to add more questions or save quiz
    keyboard = [
        [types.CallbackButton(text=texts.add_quiz_question_button, payload=callback_payload.AddQuizQuestion().pack())],
        [types.CallbackButton(text=texts.save_quiz_button, payload=callback_payload.SaveQuiz().pack())],
        [types.CallbackButton(text=texts.back, payload=callback_payload.BackToMainMenu().pack())],
    ]

    await facade.edit_message(
        text=texts.enter_quiz_questions_draft_menu.format(
            questions=format_question_list([q["text"] for q in questions]),
        ),
        keyboard=keyboard,
    )


@router.message_callback(callback_payload.DeleteQuizAnswer.filter())
async def handle_delete_quiz_answer(
    _: updates.MessageCallback,
    payload: callback_payload.DeleteQuizAnswer,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    answer_id = payload.answer_id

    answer = await dao.get_answer_by_id(answer_id=answer_id)
    if not answer:
        await facade.answer_text(texts.no_answers_available)
        return

    question = await dao.get_question_by_id(question_id=answer.question_id)
    if not question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    quiz = await dao.get_quiz_by_id(quiz_id=question.quiz_id)
    if not quiz:
        await facade.answer_text(texts.quiz_not_found)
        return

    was_correct = answer.is_correct

    await dao.delete(instance=answer)
    await dao.commit()

    remaining_answers = await dao.get_answers_by_question_id(question_id=question.id)

    if was_correct and remaining_answers:
        first_answer = remaining_answers[0]
        for current_answer in remaining_answers:
            current_answer.is_correct = current_answer.id == first_answer.id
            dao.add(instance=current_answer)

        await dao.commit()

    answers = await dao.get_answers_by_question_id(question_id=question.id)
    keyboard = keyboards.quiz_question_editor_keyboard(
        question_id=question.id,
        quiz_id=quiz.id,
        answers=answers,
    )

    await facade.edit_message(
        text=build_quiz_question_editor_text(question=question, answers=answers),
        keyboard=keyboard,
    )


@router.message_callback(callback_payload.DeleteQuiz.filter())
async def handle_delete_quiz(
    update: updates.MessageCallback,
    payload: callback_payload.DeleteQuiz,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    text = texts.delete_quiz_confirm.format(title=quiz.title)
    keyboard = keyboards.delete_quiz_confirm(quiz_id=quiz_id)

    await facade.edit_message(text=text, keyboard=keyboard)


@router.message_callback(callback_payload.DeleteQuizQuestion.filter())
async def handle_delete_quiz_question(
    update: updates.MessageCallback,
    payload: callback_payload.DeleteQuizQuestion,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    question_id = payload.question_id

    question = await dao.get_question_by_id(question_id=question_id)

    if not question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    quiz = await dao.get_quiz_by_id(quiz_id=question.quiz_id)
    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    await dao.delete(instance=question)
    await dao.commit()

    # show updated questions menu
    questions = await dao.get_questions_by_quiz_id(quiz_id=quiz.id)
    keyboard = keyboards.quiz_questions_menu_with_items(quiz_id=quiz.id, questions=questions)
    questions_text = format_question_list([q.text for q in questions])

    await facade.edit_message(text=texts.quiz_questions_menu.format(questions=questions_text), keyboard=keyboard)


@router.message_callback(callback_payload.EditQuizQuestion.filter())
async def handle_edit_quiz_question(
    _: updates.MessageCallback,
    payload: callback_payload.EditQuizQuestion,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    question_id = payload.question_id

    question = await dao.get_question_by_id(question_id=question_id)
    if not question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    answers = await dao.get_answers_by_question_id(question_id=question.id)
    keyboard = keyboards.quiz_question_editor_keyboard(
        question_id=question.id,
        quiz_id=question.quiz_id,
        answers=answers,
    )

    await facade.edit_message(
        text=build_quiz_question_editor_text(question=question, answers=answers),
        keyboard=keyboard,
    )


@router.message_callback(callback_payload.EditQuizAnswer.filter())
async def handle_edit_quiz_answer(
    _: updates.MessageCallback,
    payload: callback_payload.EditQuizAnswer,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    answer_id = payload.answer_id

    answer = await dao.get_answer_by_id(answer_id=answer_id)
    if not answer:
        await facade.answer_text(texts.no_answers_available)
        return

    # prompt for new answer text
    await state.update_data(editing_answer_id=answer.id, editing_question_id=answer.question_id)
    await state.set_state(states.EditQuizAnswer.waiting_for_text)

    await facade.edit_message(text=texts.enter_quiz_answer, keyboard=keyboards.cancel)


@router.message_callback(callback_payload.AddQuizAnswerToQuestion.filter())
async def handle_add_quiz_answer_to_question(
    _: updates.MessageCallback,
    payload: callback_payload.AddQuizAnswerToQuestion,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.update_data(adding_answer_question_id=payload.question_id)
    await state.set_state(states.AddQuizAnswerToQuestion.waiting_for_text)

    await facade.edit_message(text=texts.enter_quiz_answer, keyboard=keyboards.cancel)


@router.message_callback(callback_payload.SetQuizAnswerCorrect.filter())
async def handle_set_quiz_answer_correct(
    _: updates.MessageCallback,
    payload: callback_payload.SetQuizAnswerCorrect,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    answer = await dao.get_answer_by_id(answer_id=payload.answer_id)
    if not answer:
        await facade.answer_text(texts.no_answers_available)
        return

    question = await dao.get_question_by_id(question_id=answer.question_id)
    if not question:
        await facade.answer_text(texts.quiz_question_not_found)
        return

    answers = await dao.get_answers_by_question_id(question_id=question.id)

    for current_answer in answers:
        current_answer.is_correct = current_answer.id == answer.id
        dao.add(instance=current_answer)

    await dao.commit()

    answers = await dao.get_answers_by_question_id(question_id=question.id)
    keyboard = keyboards.quiz_question_editor_keyboard(
        question_id=question.id,
        quiz_id=question.quiz_id,
        answers=answers,
    )

    await facade.edit_message(
        text=build_quiz_question_editor_text(question=question, answers=answers),
        keyboard=keyboard,
    )


@router.message_callback(callback_payload.DeleteQuizConfirm.filter())
async def handle_delete_quiz_confirm(
    update: updates.MessageCallback,
    payload: callback_payload.DeleteQuizConfirm,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    await dao.delete(instance=quiz)
    await dao.commit()

    quizzes = await dao.get_quizzes_by_user_id(user_id=user_id)

    keyboard = keyboards.my_quizzes_keyboard(quizzes=quizzes)
    await facade.edit_message(text=texts.my_quizzes_list.format(user_quizzes_count=len(quizzes)), keyboard=keyboard)


@router.message_callback(callback_payload.AddQuizPhoto.filter())
async def handle_add_quiz_photo(
    update: updates.MessageCallback,
    payload: callback_payload.AddQuizPhoto,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    await state.update_data(quiz_id=quiz_id)
    await state.set_state(states.AddQuizPhoto.waiting_for_photo)

    await facade.edit_message(
        text=texts.send_quiz_photo,
        keyboard=keyboards.back_to_quiz(quiz_id=quiz_id),
    )


@router.message_created(filters.StateFilter(states.AddQuizPhoto.waiting_for_photo))
async def handle_save_quiz_photo(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    if not update.message.body.photo:
        await facade.answer_text(texts.send_quiz_photo_invalid)
        return

    photo = update.message.body.photo[-1]

    data = await state.get_data()
    quiz_id = data["quiz_id"]

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz:
        await facade.answer_text(texts.quiz_not_found)
        return

    quiz.photo_file_id = photo.payload.token
    dao.add(instance=quiz)
    await dao.commit()

    place_in_top = await dao.get_quiz_place_in_top(quiz_id=quiz.id)

    bot_user = await facade.get_my_info()

    if not bot_user.username:
        return

    text = texts.quiz_menu.format(title=quiz.title, usages=quiz.usages, place_in_top=place_in_top)
    keyboard = keyboards.quiz_menu(quiz=quiz, bot_username=bot_user.username)

    await facade.answer_text(text=text, keyboard=keyboard)


@router.message_callback(callback_payload.OpenQuizToProceed.filter())
async def handle_open_quiz_to_proceed(
    _: updates.MessageCallback,
    payload: callback_payload.OpenQuizToProceed,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz:
        await facade.answer_text(texts.quiz_not_found)
        return

    media = None

    if quiz.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=quiz.photo_file_id)),
        ]

    keyboard = keyboards.proceed_quiz(quiz_id=quiz_id)

    # build message with title and description
    message_text = f"<b>{quiz.title}</b>"
    if quiz.description:
        message_text += f"\n\n{quiz.description}"

    if media:
        await facade.delete_message()
        await facade.answer(text=message_text, media=media, keyboard=keyboard)

    else:
        await facade.edit_message(text=message_text, keyboard=keyboard)


@router.message_callback(callback_payload.RandomQuiz.filter())
async def handle_random_quiz(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    quiz = await dao.get_random_quiz()

    if not quiz:
        await facade.answer_text(texts.no_quizzes_available)
        return

    media = None
    if quiz.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=quiz.photo_file_id)),
        ]

    keyboard = keyboards.proceed_quiz(quiz_id=quiz.id)

    # show title + description for the random quiz
    message_text = f"<b>{quiz.title}</b>"
    if quiz.description:
        message_text += f"\n\n{quiz.description}"

    if media:
        await facade.delete_message()
        await facade.answer(text=message_text, media=media, keyboard=keyboard)
    else:
        await facade.edit_message(text=message_text, keyboard=keyboard)


@router.message_callback(callback_payload.QuizQuestions.filter())
async def handle_quiz_questions(
    update: updates.MessageCallback,
    payload: callback_payload.QuizQuestions,
    facade: MessageCallbackFacade,
    dao: DAO,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz or quiz.creator_user_id != user_id:
        await facade.answer_text(texts.quiz_not_found)
        return

    questions = await dao.get_questions_by_quiz_id(quiz_id=quiz_id)

    keyboard = keyboards.quiz_questions_menu_with_items(quiz_id=quiz_id, questions=questions)
    questions_text = format_question_list([q.text for q in questions])

    await facade.edit_message(text=texts.quiz_questions_menu.format(questions=questions_text), keyboard=keyboard)


@router.message_callback(callback_payload.ProceedQuiz.filter())
async def handle_proceed_quiz(
    update: updates.MessageCallback,
    payload: callback_payload.ProceedQuiz,
    facade: MessageCallbackFacade,
    dao: DAO,
    state: FSMContext,
) -> None:
    user_id = update.user.user_id
    quiz_id = payload.quiz_id

    quiz = await dao.get_quiz_by_id(quiz_id=quiz_id)

    if not quiz:
        await facade.answer_text(texts.quiz_not_found)
        return

    questions = await dao.get_questions_by_quiz_id(quiz_id=quiz_id)

    if not questions:
        await facade.answer_text(texts.no_questions_available)
        return

    # increment usages if not author
    if quiz.creator_user_id != user_id:
        quiz.usages += 1
        await dao.commit()

    # initialize state for quiz progression
    await state.set_state(states.ProceedQuiz.answering_question)
    await state.update_data(
        quiz_id=quiz_id,
        questions=questions,
        current_question_index=0,
        correct_answers=0,
    )

    # show first question
    question = questions[0]
    answers = await dao.get_answers_by_question_id(question_id=question.id)

    media = None
    if question.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=question.photo_file_id)),
        ]

    keyboard = keyboards.proceed_quiz_answers_keyboard(answers=answers)

    await facade.edit_message(text=question.text, media=media, keyboard=keyboard)


@router.message_callback(callback_payload.QuizAnswer.filter())
async def handle_quiz_answer(
    _: updates.MessageCallback,
    payload: callback_payload.QuizAnswer,
    facade: MessageCallbackFacade,
    state: FSMContext,
    dao: DAO,
) -> None:
    data = await state.get_data() or {}
    questions = data.get("questions", [])
    current_question_index = data.get("current_question_index", 0)
    correct_answers = data.get("correct_answers", 0)

    if current_question_index >= len(questions):
        await facade.answer_text(texts.quiz_not_found)
        return

    current_question = questions[current_question_index]

    # get selected answer by id
    selected_answer = await dao.get_answer_by_id(answer_id=payload.answer_id)

    if not selected_answer or selected_answer.question_id != current_question.id:
        await facade.answer_text(texts.quiz_not_found)
        return

    # check if answer is correct
    if selected_answer.is_correct:
        correct_answers += 1

    current_question_index += 1

    # check if there are more questions
    if current_question_index >= len(questions):
        # show results
        total_questions = len(questions)
        result_text = texts.quiz_result.format(correct=correct_answers, total=total_questions)

        await facade.edit_message(text=result_text)
        await facade.answer_text(text=texts.main_menu, keyboard=keyboards.main_menu)
        await state.clear()
        return

    # show next question
    await state.update_data(current_question_index=current_question_index, correct_answers=correct_answers)

    next_question = questions[current_question_index]
    next_answers = await dao.get_answers_by_question_id(question_id=next_question.id)

    media = None
    if next_question.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(
                payload=types.PhotoAttachmentRequestPayload(token=next_question.photo_file_id),
            ),
        ]

    keyboard = keyboards.proceed_quiz_answers_keyboard(answers=next_answers)

    await facade.edit_message(text=next_question.text, media=media, keyboard=keyboard)
