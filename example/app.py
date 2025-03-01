import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from config import settings
from handlers import main_router
from uvloop import install as install_uvloop


async def main() -> None:
    bot = Bot(settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(bot=bot)
    dp.include_routers(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    install_uvloop()
    asyncio.run(main())
