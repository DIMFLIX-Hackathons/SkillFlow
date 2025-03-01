from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.inline_keyboard import choose_mode

router = Router()

@router.message(Command("start"))
async def start_bot(message: Message):
    await message.answer("Выбери режим задания", reply_markup=choose_mode)


