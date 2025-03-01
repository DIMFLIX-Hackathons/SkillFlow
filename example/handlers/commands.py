from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def start_bot(message: Message):
    await message.answer("Переведите на английский: 'Я люблю читать книги'")

