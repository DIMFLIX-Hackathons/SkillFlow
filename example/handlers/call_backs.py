from aiogram import Router,F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "translate_practice")
async def translate_sentences(call: CallbackQuery, state: FSMContext):
    await state.update_data(state="translate_practice")
    await call.message.delete()
    await call.message.answer('"Покажи мне свой писюн"')
