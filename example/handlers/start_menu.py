from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message

on = Router()


@on.message(Command("start"))
@on.callback_query(F.data == "start_menu")
async def start_bot(obj: Message | CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()

    kb = InlineKeyboardMarkup(
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

    text = "Выбери режим задания"
    if isinstance(obj, Message):
        await bot.send_message(
            chat_id=obj.from_user.id,
            text=text,
            reply_markup=kb,
        )
        await bot.delete_message(chat_id=obj.from_user.id, message_id=obj.message_id)
    else:
        await bot.edit_message_text(
            chat_id=obj.from_user.id,
            message_id=obj.message.message_id,
            text=text,
            reply_markup=kb,
        )
