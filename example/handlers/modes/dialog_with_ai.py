import os
import tempfile
from collections import deque
from io import BytesIO

import speech_recognition as sr
from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import BufferedInputFile
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message
from config import english_system_prompt
from gtts import gTTS
from keyboards.inline_keyboard import ai_dialog_real
from keyboards.inline_keyboard import ai_dialog_text
from keyboards.inline_keyboard import to_start_menu_btn
from loguru import logger
from pydub import AudioSegment
from utils.ai_assistant import AIAssistant

on = Router()

MAX_HISTORY_LENGTH = 5
ai_assistant = AIAssistant(system_prompt=english_system_prompt)


class DialogState(StatesGroup):
    active = State()
    real_dialog = State()


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

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[ai_dialog_real], [ai_dialog_text], [to_start_menu_btn]]
    )

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text="🤖 Выберите режим",
        reply_markup=kb,
    )
    await state.set_state(DialogState.active)


@on.callback_query(F.data == "text_dialog")
async def start_text_dialog(callback: CallbackQuery, bot: Bot, state: FSMContext):
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


@on.callback_query(F.data == "real_dialog")
async def start_real_dialog(callback: CallbackQuery, bot: Bot, state: FSMContext):
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
        text="🤖 Диалоговый режим активирован!\nОтправляйте голосовое сообщение...",
        reply_markup=kb,
    )
    await state.set_state(DialogState.real_dialog)


@on.message(DialogState.active)
async def handle_dialog_message(message: Message, bot: Bot, state: FSMContext):
    user_data = await state.get_data()
    current_history = user_data.get("history", [])
    max_history = user_data.get("max_history", MAX_HISTORY_LENGTH)

    await bot.send_chat_action(message.chat.id, "typing")

    response, new_history = await ai_assistant.process_message(
        user_message=message.text, history=current_history
    )

    trimmed_history = _trim_history(new_history, max_history)

    kb = InlineKeyboardMarkup(inline_keyboard=[[to_start_menu_btn]])
    await state.update_data(history=trimmed_history)
    await message.answer(response, reply_markup=kb)


@on.message(DialogState.real_dialog)
async def handle_real_dialog_message(
    message: types.Message, bot: Bot, state: FSMContext
):
    try:
        if not message.voice:
            await message.reply("Пожалуйста, отправьте голосовое сообщение")
            return

        voice_file = await bot.get_file(message.voice.file_id)
        downloaded_file = await bot.download_file(voice_file.file_path)

        with tempfile.NamedTemporaryFile(delete=False) as tmp_ogg:
            tmp_ogg.write(downloaded_file.read())
            ogg_audio = AudioSegment.from_ogg(tmp_ogg.name)
            wav_data = ogg_audio.export(format="wav").read()

        r = sr.Recognizer()
        with sr.AudioFile(BytesIO(wav_data)) as source:
            audio_data = r.record(source)
            try:
                user_text = r.recognize_google(audio_data, language="ru-RU")
            except sr.UnknownValueError:
                await message.reply("Не удалось распознать речь")
                return

        user_data = await state.get_data()
        current_history = user_data.get("history", [])
        response, new_history = await ai_assistant.process_message(
            user_message=user_text, history=current_history
        )
        response = response[:-1]

        tts = gTTS(text=response, lang="en")
        mp3_buffer = BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        audio = AudioSegment.from_mp3(mp3_buffer)
        ogg_buffer = BytesIO()
        audio.export(ogg_buffer, format="ogg", codec="libopus")
        ogg_data = ogg_buffer.getvalue()

        await message.reply_voice(
            voice=BufferedInputFile(file=ogg_data, filename="response.ogg"),
            caption=f"Ваш запрос: {user_text}\nОтвет: {response}",
        )

        os.unlink(tmp_ogg.name)

    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")
        logger.error(f"Error in handle_dialog_message: {str(e)}")
