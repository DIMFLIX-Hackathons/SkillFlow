import os

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from models.recognize import compare_pronunciation

on = Router()


@on.message()
async def check_audio(bot: Bot, message: Message):
    audio = message.voice

    file_id = audio.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    save_path = os.path.join("voices", f"{message.from_user.id}_1.ogg")
    await message.bot.download_file(file_path, save_path)
    distance = compare_pronunciation(save_path)
    await bot.send_message(
        chat_id=message.from_user.id, text=f"{distance} - Евклидово расстояние"
    )
    # await message.answer(f"{words} - слова")
