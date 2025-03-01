from aiogram import Bot, Dispatcher
from config import settings
import asyncio
# from b/ot.logger import cl
from handlers.commands import router as r_h
from handlers.messages import router as r_m

async def main() -> None:

    bot = Bot(settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    # dp.update.middleware(UserMiddleware())
    dp.include_routers(
        r_h,
        r_m
    )
    #     wcbr,
    #     wr,
    #     router,
    #     router_mc,
    #     router_m,
    #     router_call_back,
    #     router_top
    # )
    await bot.delete_webhook(True)
    # with open("words.json", "r", encoding="UTF-8") as f:
    #     game.wordlie.words = json.load(f)
    #     f.close()
    # cl.custom_logger.debug("Бот запущен", extra={"username": "SYSTEM",
    #                                    "state": "nothing",
    #                                    "handler_name": "MAIN",
    #                                    "params":"nothing"})
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
