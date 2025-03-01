import os
from collections import deque

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
from pydantic import ValidationError
from utils.translation_manager import TranslationPracticeManager


class PracticeState(StatesGroup):
    select_level = State()
    active_session = State()
    phrase_history = State()


class PracticeSession(BaseModel):
    current_phrase: str
    target_translation: str
    attempts: int = 0
    history: deque = deque(maxlen=100)
    level: str = "B1"


CORRECT_LANGUAGE = "en"
manager = TranslationPracticeManager()
on = Router()


def get_levels_keyboard():
    builder = InlineKeyboardBuilder()
    for level in manager.levels:
        builder.button(text=level, callback_data=f"level_{level}")
    builder.adjust(3)
    builder.row(to_start_menu_btn)
    return builder.as_markup()


@on.callback_query(F.data == "translate_practice")
async def start_practice(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(PracticeState.select_level)
    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text="📚 Выберите уровень сложности:",
        reply_markup=get_levels_keyboard(),
    )


@on.callback_query(F.data.startswith("level_"))
async def select_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    user_id = callback.from_user.id
    data = await state.get_data()

    history = data.get("phrase_history", deque(maxlen=100))

    try:
        phrase = await manager.generate_phrase(user_id, list(history), level)
        history.append(phrase["ru"])

        session = PracticeSession(
            current_phrase=phrase["ru"],
            target_translation=phrase["en"],
            history=history,
            level=level,
        )

        await state.update_data(current_session=session.dict(), phrase_history=history)
        await state.set_state(PracticeState.active_session)

        builder = InlineKeyboardBuilder()
        builder.add(to_start_menu_btn)

        await callback.bot.send_message(
            user_id,
            f"📝 Уровень {level}\nПереведите на английский:\n\n{phrase['ru']}",
            reply_markup=builder.as_markup(),
        )
    except Exception as e:
        logger.error(f"Session start failed: {str(e)}")
        await callback.message.answer("⚠️ Произошла ошибка, попробуйте позже")


@on.message(F.voice, PracticeState.active_session)
async def handle_voice_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.add(to_start_menu_btn)

    try:
        session = PracticeSession(**data["current_session"])
    except (KeyError, ValidationError):
        await message.answer("⚠️ Сессия повреждена, начните заново")
        return

    # Загрузка и обработка аудио
    try:
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        audio_path = CACHE_FOLDER / f"voice_{user_id}_{message.message_id}.ogg"
        await message.bot.download_file(file.file_path, destination=audio_path)

        history = data.get("phrase_history", deque(maxlen=100))
        rec_lang, rec_text = await manager.process_audio(str(audio_path))
        if rec_lang == CORRECT_LANGUAGE:
            is_correct = await manager.validate_answer(
                rec_text, session.target_translation
            )

            if is_correct:
                next_phrase = await manager.generate_phrase(
                    user_id=user_id, history=list(history), level=session.level
                )
                history.append(next_phrase["ru"])
                session.current_phrase = next_phrase["ru"]
                session.target_translation = next_phrase["en"]
                session.history = history

                response = (
                    f"✅ Отлично! Ваш ответ подходит!\n"
                    f"Вы сказали: {rec_text}\n"
                    f"Теперь попробуйте сказать: {next_phrase['ru']}"
                )
            else:
                session.attempts += 1
                response = (
                    f"❌ Попробуйте ещё раз. Ваш ответ: {rec_text}\n"
                    f"Правильный вариант: {session.target_translation}"
                )
        else:
            session.attempts += 1
            response = (
                f"❌ Попробуйте ещё раз. Ваш ответ: {rec_text}\n"
                f"Правильный вариант: {session.target_translation}"
            )

        await state.update_data(
            current_session=session.model_dump(), phrase_history=history
        )
        await message.answer(response, reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        await message.answer("⚠️ Ошибка обработки, попробуйте ещё раз")
    finally:
        if audio_path:
            os.remove(audio_path)
