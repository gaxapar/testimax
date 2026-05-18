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

    await state.update_data(title=update.text, questions=[])
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
    questions = data.get("questions", [])

    if not title:
        await facade.answer_text(text=texts.enter_quiz_title_invalid)
        return

    if not questions:
        await facade.answer_text(texts.no_questions_available)
        return

    # create quiz
    quiz = models.Quiz(title=title, creator_user_id=user_id)
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
        text=texts.quiz_questions_menu.format(questions=", ".join(q["text"] for q in questions)),
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

    if media:
        await facade.delete_message()
        await facade.answer(text=quiz.title, media=media, keyboard=keyboard)

    else:
        await facade.edit_message(text=quiz.title, keyboard=keyboard)


@router.message_callback(callback_payload.ProceedQuiz.filter())
async def handle_proceed_quiz(
    update: updates.MessageCallback,
    payload: callback_payload.ProceedQuiz,
    facade: MessageCallbackFacade,
    dao: DAO,
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

    # present first question for simplicity
    question = questions[0]
    answers = await dao.get_answers_by_question_id(question_id=question.id)

    media = None
    if question.photo_file_id:
        media = [
            types.PhotoAttachmentRequest(payload=types.PhotoAttachmentRequestPayload(token=question.photo_file_id)),
        ]

    # build answers text
    answers_text = "\n".join(f"{i + 1}. {a.text}" for i, a in enumerate(answers))

    await facade.delete_message()
    await facade.answer(text=f"{question.text}\n\n{answers_text}", media=media)

    await facade.answer_text(text=texts.main_menu, keyboard=keyboards.main_menu)
