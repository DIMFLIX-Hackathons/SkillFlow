from aiogram import Bot, Dispatcher
from config import settings
import asyncio
# from b/ot.logger import cl
from handlers.commands import router as r_h
from handlers.messages import router as r_m
from handlers.call_backs import router as r_cb

async def main() -> None:

    bot = Bot(settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(
        r_h,
        r_m,
        r_cb
    )
    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

