from aiogram import Router
from aiogram.types import Message
import os
from models.recognize import compare_pronunciation

router = Router()

@router.message()
async def check_audio(message: Message):
    audio = message.voice

    file_id = audio.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    save_path = os.path.join("voices", f"{message.from_user.id}_1.ogg")
    await message.bot.download_file(file_path, save_path)
    distance = compare_pronunciation(save_path)
    await message.answer(f"{distance} - Евклидово расстояние")
    # await message.answer(f"{words} - слова")