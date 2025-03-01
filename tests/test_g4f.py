import asyncio

import g4f


class AsyncG4FChat:
    def __init__(self):
        self.history: list[dict] = []
        self.model = "deepseek-chat"  # Модель DeepSeek v3

    def _trim_history(self, max_length: int = 6):
        """Обрезаем историю до последних max_length сообщений"""
        if len(self.history) > max_length:
            self.history = self.history[-max_length:]

    async def ask(self, message: str, max_retries: int = 3) -> str:
        self.history.append({"role": "user", "content": message})
        full_response = ""

        for attempt in range(max_retries):
            try:
                response = await g4f.ChatCompletion.create_async(
                    model=self.model,
                    messages=self.history,
                    stream=False,  # Отключаем потоковый вывод
                )

                if response:
                    full_response = response
                    self.history.append({"role": "assistant", "content": full_response})
                    self._trim_history()
                    return full_response

            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Ошибка: {str(e)}"
                await asyncio.sleep(1)

        return "Не удалось получить ответ"


async def main():
    chat = AsyncG4FChat()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break

            if not user_input:
                continue

            response = await chat.ask(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    asyncio.run(main())
