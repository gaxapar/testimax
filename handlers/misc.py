from maxo.errors.api import MaxBotBadRequestError
from maxo.fsm.context import FSMContext
from maxo.routing import filters, updates
from maxo.routing.facades import MessageCallbackFacade, MessageCreatedFacade
from maxo.routing.routers.simple import Router

import keyboards
import states
import texts
from keyboards import callback_payload

router = Router()


async def _safe_edit_main_menu(facade: MessageCallbackFacade) -> None:
    try:
        await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)
    except MaxBotBadRequestError as error:
        if "error.edit.invalid.message" not in str(error):
            raise

        await facade.answer_text(text=texts.main_menu, keyboard=keyboards.main_menu)


@router.message_callback(callback_payload.BackToMainMenu.filter())
async def handle_back_to_main_menu(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await _safe_edit_main_menu(facade=facade)


@router.message_callback(callback_payload.Cancel.filter())
async def handle_cancel(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await _safe_edit_main_menu(facade=facade)



@router.message_created(filters.Command("file_id"))
async def handle_get_file_id_command(
    _: updates.MessageCreated,
    facade: MessageCreatedFacade,
    state: FSMContext,
) -> None:
    await state.set_state(states.GetPhotoFileId.waiting_for_photo)

    await facade.answer_text(text="Отправь фото, чтобы получить его file_id")


@router.message_created(filters.StateFilter(states.GetPhotoFileId.waiting_for_photo))
async def handle_get_file_id(
    update: updates.MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    if update.text and update.text == "/cancel":
        await facade.answer_text(text="Отмена получения file_id")
        return

    if not (photo := update.message.body.photo):
        await facade.answer_text(text="Сообщение не содержит файл")
        return

    file_id = photo[-1].payload.token
    await facade.answer_text(text=file_id)

    await facade.answer_text(text="Когда закончишь, нажми /cancel")
