import asyncio
import datetime

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from config import settings
from src.core.schedule.service import ScheduleService
from src.core.users.schemas import SUser
from src.core.users.service import UsersService, ChatsService

router = Router()


@router.message(Command(commands=["Расписание"]))
async def schedule_from_user(message: types.Message):
    user = await UsersService.get_by_id(message.from_user.id)
    if not user:
        await message.answer(text="Сначала зарегистрируйся")
    service = ScheduleService(user)
    image = service.create_schedule()
    document = BufferedInputFile(image, filename=f"{user.name}_schedule.png")
    await message.answer_document(
        document=document,
    )


async def send_common_schedule(bot: Bot):
    chats = await ChatsService.get_list()
    for chat in chats:
        user = SUser(
            id=1,
            name="Общее",
            group_name=chat.group_name,
            department_name=chat.department_name
        )
        service = ScheduleService(user)
        image = service.create_schedule()

        document = BufferedInputFile(image, filename=f"{user.name}_schedule.png")
        await bot.send_document(
            chat_id=chat.id,
            document=document,
        )


async def wait_until_monday(bot: Bot):
    while True:
        now = datetime.datetime.now()
        if now.weekday() == 5 and now.hour == 13 and now.minute == 53:
            await send_common_schedule(bot)
            await asyncio.sleep(60)  # Ждем 60 секунд, чтобы избежать повторного выполнения
        await asyncio.sleep(60)  # Ждем 60 секунд перед следующей проверкой
