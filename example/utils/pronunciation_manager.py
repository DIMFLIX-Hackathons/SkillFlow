import json
from typing import Dict
from typing import Set

import torch
from loguru import logger
from transformers import pipeline
from utils.ai_assistant import AIAssistant


class PronunciationPracticeManager:
    def __init__(self):
        self.levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        self.max_history = 20
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.g2p_processor = pipeline(
            "automatic-speech-recognition",
            model="dg96/whisper-finetuning-phoneme-transcription-g2p-large-dataset-space-seperated-phonemes",
            device=self.device,
        )
        self.ai_assistant = AIAssistant(
            system_prompt="Generate unique English phrases for pronunciation practice with ARPABET phonemes."
        )

    async def generate_phrase(
        self, level: str, used_phrases: Set[str]
    ) -> Dict[str, str]:
        for _ in range(3):
            try:
                prompt = (
                    f"Generate a {level}-level English phrase for pronunciation practice. "
                    "Provide the phrase and its ARPABET phonemes separated by spaces. "
                    "Phrase must be unique and not from this list: ["
                    f"{', '.join(list(used_phrases)) if used_phrases else 'None'}].\n"
                    'Strict JSON format: {"phrase": "...", "phonemes": "..."}'
                )

                response, _ = await self.ai_assistant.process_message(prompt, [])
                phrase_data = await self.safe_json_parse(response)

                if phrase_data["phrase"] not in used_phrases:
                    return phrase_data

                logger.warning(f"Duplicate phrase: {phrase_data['phrase']}")

            except Exception as e:
                logger.error(f"Generation attempt {_ + 1} failed: {str(e)}")

        return self._get_fallback_phrase(used_phrases)

    async def safe_json_parse(self, json_str: str) -> Dict[str, str]:
        try:
            data = json.loads(json_str.strip().strip("`"))
            if not all(key in data for key in ["phrase", "phonemes"]):
                raise ValueError("Invalid keys")
            return data
        except Exception as e:
            logger.error(f"JSON parse error: {str(e)}")
            return self._get_fallback_phrase(set())

    def _get_fallback_phrase(self, used_phrases: Set[str]) -> Dict[str, str]:
        fallbacks = [
            {
                "phrase": "Artificial intelligence",
                "phonemes": "AA R T AH F IH SH AH L IH N T EH L AH JH AH N S",
            },
            {"phrase": "Machine learning", "phonemes": "M AH SH IY N L ER N IH NG"},
            {
                "phrase": "Natural language processing",
                "phonemes": "N AE CH ER AH L L AE NG G W AH JH P R AA S EH S IH NG",
            },
        ]
        for fb in fallbacks:
            if fb["phrase"] not in used_phrases:
                return fb
        return fallbacks[0]

    async def get_phonemes(self, audio_path: str) -> str:
        result = self.g2p_processor(str(audio_path), generate_kwargs={"language": "en"})
        return result["text"].strip()
