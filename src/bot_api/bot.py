from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import settings

from src.bot_api.handlers.schedule  import router as schedule_router
from src.bot_api.handlers.login import router as login_router
from src.bot_api.handlers.chats  import router as chat_router
from src.bot_api.keyboards.reply_kb import main_kb



bot = Bot(
    token=settings.TOKEN,
    timeout=180,
)
dp = Dispatcher()
dp.include_router(schedule_router)
dp.include_router(chat_router)
dp.include_router(login_router)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.reply(text='Привет, чем могу помочь?', reply_markup=main_kb)
