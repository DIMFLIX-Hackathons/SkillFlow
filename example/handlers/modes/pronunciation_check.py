from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup
from keyboards.inline_keyboard import to_start_menu_btn

on = Router()


@on.callback_query(F.data == "pronunciation_check")
async def pronunciation_check(callback: CallbackQuery, bot: Bot) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[[to_start_menu_btn]])

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text="Хендлер еще не написан...",
        reply_markup=kb,
    )
