import os
from typing import List
from typing import Set

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CACHE_FOLDER
from keyboards.inline_keyboard import to_start_menu_btn
from loguru import logger
from pydantic import BaseModel
from utils.pronunciation_manager import PronunciationPracticeManager


class PronunciationState(StatesGroup):
    select_level = State()
    active_session = State()


class PronunciationSession(BaseModel):
    current_phrase: str
    target_phonemes: str
    history: List[str] = []
    used_phrases: Set[str] = set()
    level: str = "B1"


manager = PronunciationPracticeManager()
router = Router()


def get_levels_keyboard():
    builder = InlineKeyboardBuilder()
    for level in manager.levels:
        builder.button(text=level, callback_data=f"pron_level_{level}")
    builder.adjust(3)
    builder.row(to_start_menu_btn)
    return builder.as_markup()


@router.callback_query(F.data == "pronunciation_check")
async def start_practice(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PronunciationState.select_level)
    await callback.message.edit_text(
        "🎯 Выберите уровень сложности:", reply_markup=get_levels_keyboard()
    )


@router.callback_query(F.data.startswith("pron_level_"))
async def handle_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[-1]
    data = await state.get_data()

    try:
        session_data = data.get("session", {})
        used_phrases = set(session_data.get("used_phrases", []))

        phrase_data = await manager.generate_phrase(level, used_phrases)
        used_phrases.add(phrase_data["phrase"])

        session = PronunciationSession(
            current_phrase=phrase_data["phrase"],
            target_phonemes=phrase_data["phonemes"],
            level=level,
            used_phrases=used_phrases,
            history=[phrase_data["phrase"]],
        )

        await state.update_data(session=session.dict())
        await state.set_state(PronunciationState.active_session)

        builder = InlineKeyboardBuilder()
        builder.add(to_start_menu_btn)

        await callback.message.edit_text(
            f"🔊 Произнесите фразу:\n\n{phrase_data['phrase']}",
            reply_markup=builder.as_markup(),
        )

    except Exception as e:
        logger.error(f"Session start error: {str(e)}")
        await callback.message.answer("⚠️ Ошибка, попробуйте позже")


@router.message(F.voice, PronunciationState.active_session)
async def handle_voice(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    data = await state.get_data()
    session = PronunciationSession(**data["session"])

    try:
        # Download audio
        voice = message.voice
        file = await bot.get_file(voice.file_id)
        audio_path = CACHE_FOLDER / f"pron_{user_id}_{message.message_id}.ogg"
        await bot.download_file(file.file_path, destination=audio_path)

        # Process audio
        user_phonemes = await manager.get_phonemes(audio_path)
        target_phonemes = session.target_phonemes.split()

        # Calculate accuracy
        user_phonemes_list = user_phonemes.split()
        correct = sum(1 for u, t in zip(user_phonemes_list, target_phonemes) if u == t)
        accuracy = round(correct / len(target_phonemes) * 100, 1)

        # Generate new phrase
        new_phrase = await manager.generate_phrase(session.level, session.used_phrases)
        session.used_phrases.add(new_phrase["phrase"])
        session.history.append(new_phrase["phrase"])

        # Prepare feedback
        feedback = (
            f"🎯 Точность: {accuracy}%\n\n"
            f"🗣 Ваш вариант:\n{user_phonemes}\n\n"
            f"🎧 Эталон:\n{session.target_phonemes}"
        )

        # Update session
        session.current_phrase = new_phrase["phrase"]
        session.target_phonemes = new_phrase["phonemes"]

        builder = InlineKeyboardBuilder()
        builder.add(to_start_menu_btn)

        await message.answer(
            f"{feedback}\n\n🔊 Новая фраза:\n{new_phrase['phrase']}",
            reply_markup=builder.as_markup(),
        )

        await state.update_data(session=session.model_dump())
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        await message.answer("⚠️ Ошибка обработки")
    finally:
        if audio_path.exists():
            os.remove(audio_path)
