import g4f


class AIAssistant:
    def __init__(
        self,
        system_prompt: str = "You're a useful assistant. Answer briefly and politely.",
    ) -> None:
        self.system_prompt = [{"role": "system", "content": system_prompt}]

    async def process_message(
        self, user_message: str, history: list[dict], model: str = "deepseek-chat"
    ) -> tuple[str, list[dict]]:
        updated_history = self.system_prompt + history.copy()
        updated_history.append(
            {
                "role": "user",
                "content": user_message + "give me an answer without a single emoji",
            }
        )

        try:
            response = await g4f.ChatCompletion.create_async(
                model=model, messages=updated_history, stream=False
            )

            updated_history.append({"role": "assistant", "content": response})
            return response, updated_history

        except Exception as e:
            return f"⚠️ Error: {str(e)}", history
