import json
import logging
import os
from collections import deque
from typing import Dict
from typing import List

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
from pydantic import BaseModel
from transformers import pipeline
from utils.ai_assistant import AIAssistant

logger = logging.getLogger(__name__)


class PronunciationState(StatesGroup):
    select_level = State()
    active_session = State()
    phrase_history = State()


class PronunciationSession(BaseModel):
    current_phrase: str
    target_phonemes: str
    history: deque = deque(maxlen=50)
    level: str = "B1"


class PronunciationPracticeManager:
    def __init__(self):
        self.levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        self.g2p_processor = pipeline(
            "automatic-speech-recognition",
            model="dg96/whisper-finetuning-phoneme-transcription-g2p-large-dataset-space-seperated-phonemes",
            device="cuda:0",
        )
        self.ai_assistant = AIAssistant(
            system_prompt="Generate English phrases for pronunciation practice with ARPABET phonemes."
        )

    async def generate_phrase(self, level: str, history: List[str]) -> Dict[str, str]:
        prompt = (
            f"Generate a {level}-level English phrase for pronunciation practice. "
            "Provide the phrase and its ARPABET phonemes separated by spaces. "
            'Format: {"phrase": "...", "phonemes": "..."}\n'
            f"Previous phrases: {', '.join(history) if history else 'None'}"
        )

        try:
            response, _ = await self.ai_assistant.process_message(prompt, [])
            return await self.safe_json_parse(response)
        except Exception as e:
            logger.error(f"Phrase generation failed: {str(e)}")
            return self._get_fallback_phrase()

    async def safe_json_parse(self, json_str: str) -> Dict[str, str]:
        try:
            data = json.loads(json_str)
            if not all(key in data for key in ["phrase", "phonemes"]):
                return self._get_fallback_phrase()
            return data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return self._get_fallback_phrase()

    def _get_fallback_phrase(self) -> Dict[str, str]:
        return {"phrase": "Hello world", "phonemes": "HH AH L OW W ER L D"}

    async def get_phonemes(self, audio_path: str) -> str:
        result = self.g2p_processor(audio_path, generate_kwargs={"language": "en"})
        return result["text"].strip()


pronunciation_manager = PronunciationPracticeManager()
pronunciation_router = Router()


def get_pronunciation_levels_kb():
    builder = InlineKeyboardBuilder()
    for level in pronunciation_manager.levels:
        builder.button(text=level, callback_data=f"pron_level_{level}")
    builder.adjust(3)
    builder.row(to_start_menu_btn)
    return builder.as_markup()


@pronunciation_router.callback_query(F.data == "pronunciation_check")
async def start_pronunciation_check(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PronunciationState.select_level)
    await callback.message.edit_text(
        "🎯 Выберите уровень сложности:", reply_markup=get_pronunciation_levels_kb()
    )


@pronunciation_router.callback_query(F.data.startswith("pron_level_"))
async def handle_level_selection(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[-1]
    data = await state.get_data()

    history = data.get("pron_history", deque(maxlen=50))

    try:
        phrase_data = await pronunciation_manager.generate_phrase(level, list(history))
        history.append(phrase_data["phrase"])

        session = PronunciationSession(
            current_phrase=phrase_data["phrase"],
            target_phonemes=phrase_data["phonemes"],
            history=history,
            level=level,
        )

        await state.update_data(current_session=session.dict(), pron_history=history)
        await state.set_state(PronunciationState.active_session)

        builder = InlineKeyboardBuilder()
        builder.add(to_start_menu_btn)

        await callback.message.edit_text(
            f"🔊 Произнесите фразу:\n\n{phrase_data['phrase']}",
            reply_markup=builder.as_markup(),
        )
    except Exception as e:
        logger.error(f"Session start failed: {str(e)}")
        await callback.message.answer("⚠️ Произошла ошибка, попробуйте позже")


@pronunciation_router.message(F.voice, PronunciationState.active_session)
async def handle_pronunciation_voice(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    session = PronunciationSession(**data["current_session"])

    try:
        # Download audio
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        audio_path = CACHE_FOLDER / f"pron_{user_id}_{message.message_id}.ogg"
        await message.bot.download_file(file.file_path, destination=audio_path)

        # Get user's phonemes
        user_phonemes = await pronunciation_manager.get_phonemes(str(audio_path))

        # Calculate accuracy
        target_phonemes = session.target_phonemes.split()
        user_phonemes_list = user_phonemes.split()

        correct = sum(1 for u, t in zip(user_phonemes_list, target_phonemes) if u == t)
        accuracy = round(correct / len(target_phonemes) * 100, 1)

        feedback = (
            f"🎯 Точность произношения: {accuracy}%\n\n"
            f"Ваши фонемы:\n{user_phonemes}\n\n"
            f"Эталонные фонемы:\n{session.target_phonemes}"
        )

        # Generate new phrase
        new_phrase = await pronunciation_manager.generate_phrase(
            session.level, list(session.history)
        )
        session.current_phrase = new_phrase["phrase"]
        session.target_phonemes = new_phrase["phonemes"]

        await state.update_data(current_session=session.dict())

        builder = InlineKeyboardBuilder()
        builder.add(to_start_menu_btn)

        await message.answer(
            f"{feedback}\n\n🔊 Новая фраза:\n{new_phrase['phrase']}",
            reply_markup=builder.as_markup(),
        )

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        await message.answer("⚠️ Ошибка обработки, попробуйте ещё раз")
    finally:
        if audio_path:
            os.remove(audio_path)
