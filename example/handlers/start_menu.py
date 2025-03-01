from aiogram import Bot
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message

on = Router()


@on.message(Command("start"))
async def start_bot(bot: Bot, message: Message):
    choose_mode = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перевести предложения",
                    callback_data="translate_practice",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Режим диалога с ИИ", callback_data="dialog_with_ai"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Проверка произношения", callback_data="pronunciation_check"
                )
            ],
        ]
    )

    await bot.send_message(
        chat_id=message.from_user.id,
        text="Выбери режим задания",
        reply_markup=choose_mode.as_markup(),
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
