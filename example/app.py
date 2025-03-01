import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from config import settings
from handlers import main_router
from loguru import logger
from uvloop import install as install_uvloop


async def on_startup() -> None:
    logger.success("Bot started successfully!")


async def on_shutdown() -> None:
    logger.success("Bot stopped successfully!")


async def main() -> None:
    bot = Bot(settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(bot=bot)
    dp.include_routers(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    install_uvloop()
    asyncio.run(main())
