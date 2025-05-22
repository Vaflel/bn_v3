from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.bot_api.keyboards.chats_keyboard import chats_keyboard
from src.bot_api.keyboards.login_kb import select_department_kb
from src.bot_api.keyboards.login_kb import departments_short_names
from src.core.users.schemas import SGroupChat
from src.core.users.service import ChatsService

router = Router()


class ChatForm(StatesGroup):
    group_name = State()
    department_name = State()


@router.message(Command(commands=["chat"]))
async def chat_menu(message: types.Message):
    await message.answer(
        text="Меню чата:".center(40),
        reply_markup=chats_keyboard
    )


@router.callback_query(lambda c: c.data == "delete")
async def delete_chat(callback: types.CallbackQuery):
    existed_chat = await ChatsService.get_by_id(callback.message.chat.id)
    if existed_chat:
        await ChatsService.delete_chat(callback.message.chat.id)
        await callback.message.answer("Чат удалён из рассылки")
    else:
        await callback.message.answer("Чат не участвует в рассылке")


@router.callback_query(lambda c: c.data == "add")
async def create_chat(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    print(f"Chat ID: {chat_id}")  # Debugging line
    existed_chat = await ChatsService.get_by_id(chat_id)
    if existed_chat:
        await callback.message.answer("Чат уже добавлен в рассылку")
    else:
        await callback.message.answer("Введи название группы")
        await state.set_state(ChatForm.group_name)


@router.message(ChatForm.group_name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(group_name=message.text)
    await state.set_state(ChatForm.department_name)
    await message.answer(text=f"Хорошо, выбери свой факультет", reply_markup=select_department_kb)


@router.callback_query(ChatForm.department_name)
async def process_department_name(callback: types.CallbackQuery, state: FSMContext):
    department_name = next((key for key, value in departments_short_names.items() if value == callback.data), None)
    data = await state.update_data(department_name=department_name)
    await state.set_state(ChatForm.group_name)

    chat = SGroupChat(
        chat_id=callback.message.chat.id,
        group_name=data.get("group_name"),
        department_name=data.get("department_name")
    )
    await ChatsService.create_chat(chat)
    await state.clear()
    await callback.message.answer(text="Чат добавлен в рассылку")
