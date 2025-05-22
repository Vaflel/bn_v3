import asyncio

from src.bot_api.bot import bot, dp
from src.bot_api.handlers.schedule import wait_until_monday


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(wait_until_monday(bot))
    await dp.start_polling(bot)


asyncio.run(main())
