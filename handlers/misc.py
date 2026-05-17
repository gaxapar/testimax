from maxo.fsm.context import FSMContext
from maxo.routing import updates
from maxo.routing.facades import MessageCallbackFacade
from maxo.routing.routers.simple import Router

import keyboards
import texts
from keyboards import callback_payload

router = Router()


@router.message_callback(callback_payload.BackToMainMenu.filter())
async def handle_back_to_main_menu(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)


@router.message_callback(callback_payload.Cancel.filter())
async def handle_cancel(
    _: updates.MessageCallback,
    facade: MessageCallbackFacade,
    state: FSMContext,
) -> None:
    await state.clear()
    await facade.edit_message(text=texts.main_menu, keyboard=keyboards.main_menu)
