
from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message
from config import english_system_prompt
from keyboards.inline_keyboard import to_start_menu_btn
from utils.ai_assistant import AIAssistant

on = Router()

MAX_HISTORY_LENGTH = 5
ai_assistant = AIAssistant(system_prompt=english_system_prompt)


class DialogState(StatesGroup):
    active = State()


def _trim_history(history: list[dict], max_length: int) -> list[dict]:
    """Обрезает историю, сохраняя последние N сообщений"""
    start_index = max(0, len(history) - max_length)
    return history[start_index:]


@on.callback_query(F.data == "dialog_with_ai")
async def start_dialog(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_data(
        {
            "history": [],
            "max_history": MAX_HISTORY_LENGTH,
        }
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[[to_start_menu_btn]])

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text="🤖 Диалоговый режим активирован!\nОтправляйте сообщения...",
        reply_markup=kb,
    )
    await state.set_state(DialogState.active)


@on.message(DialogState.active)
async def handle_dialog_message(message: Message, bot: Bot, state: FSMContext):
    user_data = await state.get_data()
    current_history = user_data.get("history", [])
    max_history = user_data.get("max_history", MAX_HISTORY_LENGTH)

    await bot.send_chat_action(message.chat.id, "typing")

    # Получаем ответ от нейросети
    response, new_history = await ai_assistant.process_message(
        user_message=message.text, history=current_history
    )

    # Обрезаем историю согласно настройкам
    trimmed_history = _trim_history(new_history, max_history)

    # Сохраняем обновленную историю
    kb = InlineKeyboardMarkup(inline_keyboard=[[to_start_menu_btn]])
    await state.update_data(history=trimmed_history)
    await message.answer(response, reply_markup=kb)
