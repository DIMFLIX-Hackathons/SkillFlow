import json
from typing import Dict
from typing import List

import torch
import whisper
from loguru import logger

from .ai_assistant import AIAssistant


class TranslationPracticeManager:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = whisper.load_model("base").to(self.device)
        self.ai_assistant = AIAssistant(
            system_prompt="You're an English teaching assistant. Generate translation tasks "
            "considering user's level. Be flexible with correct variations. Never repeat phrases."
        )
        self.levels = ["A1", "A2", "B1", "B2", "C1", "C2"]

    async def generate_phrase(
        self, user_id: int, history: List[str], level: str
    ) -> Dict[str, str]:
        history_prompt = f"Previous phrases: {', '.join(history)}" if history else ""
        prompt = (
            f"Generate a {level}-level Russian phrase for translation practice "
            f'with its English translation. Use format: {{"ru": "...", "en": "..."}}\n'
            f"{history_prompt}"
        )

        try:
            response, _ = await self.ai_assistant.process_message(prompt, [])
            return await self.safe_json_parse(response.strip())
        except Exception as e:
            logger.error(f"Phrase generation failed: {str(e)}")
            return {"ru": "Привет, как дела?", "en": "Hello, how are you?"}

    async def safe_json_parse(self, json_str: str) -> Dict[str, str]:
        try:
            data = json.loads(json_str)
            if not all(key in data for key in ["ru", "en"]):
                raise ValueError("Invalid keys in generated response")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise

    async def validate_answer(self, user_answer: str, target: str) -> bool:
        prompt = (
            f"Check if '{user_answer}' has same meaning as '{target}'. "
            f"Consider grammar variations. Answer only yes/no."
        )
        try:
            response, _ = await self.ai_assistant.process_message(prompt, [])
            return "yes" in response.lower()
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False

    async def process_audio(self, audio_path: str) -> tuple[str]:
        result = self.whisper_model.transcribe(
            audio_path, temperature=0, fp16=bool(self.device == "cuda")
        )
        return (result["language"], result["text"].strip().lower())
