from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from keyboards.inline_keyboard import to_start_menu_btn

on = Router()


@on.callback_query(F.data == "dialog_with_ai")
async def dialog_with_ai(bot: Bot, callback: CallbackQuery) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[[to_start_menu_btn]])

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text="Хендлер еще не написан...",
        reply_markup=kb.as_markup(),
    )
