from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from aiogram.filters import Command

from src.bot_api.keyboards.reply_kb import main_kb
from src.bot_api.keyboards.login_kb import departments_short_names
from src.core.users.service import UsersService
from src.core.users.schemas import SUser
from src.bot_api.keyboards.login_kb import select_department_kb, user_exist_keyboard

router = Router()


class UserForm(StatesGroup):
    name = State()
    department_name = State()
    group_name = State()


@router.message(Command(commands=["отмена"]))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(text="Отменено")


@router.message(Command(commands=["Оставить"]))
async def keep_user(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="Существующий пользователь оставлен. Вы можете продолжить использовать бота.",
        reply_markup=main_kb
    )


@router.message(Command(commands=["Удалить"]))
async def delete_user(message: types.Message, state: FSMContext) -> None:
    await UsersService.delete_user(message.from_user.id)
    await state.set_state(UserForm.name)
    text = "Введи своё имя в формате Иванов И."
    await message.answer(text=text)


@router.message(Command(commands=["login"]))
async def login(message: types.Message, state: FSMContext) -> None:
    existed_user = await UsersService.get_by_id(message.from_user.id)
    if existed_user:
        text = f"К этому аккаунту Telegram уже привязан пользователь: {existed_user.name}, {existed_user.group_name}, {existed_user.department_name} Вы можете удалить и создать нового, либо оставить текущего"
        await message.answer(text=text, reply_markup=user_exist_keyboard)
    else:
        await state.set_state(UserForm.name)
        text = "Введи своё имя в формате Иванов И."
        await message.answer(text=text)


@router.message(UserForm.name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(UserForm.department_name)
    await message.answer(text=f"Хорошо, выбери свой факультет", reply_markup=select_department_kb)


@router.callback_query(UserForm.department_name)
async def process_department_name(callback: types.CallbackQuery, state: FSMContext):
    department_name = next((key for key, value in departments_short_names.items() if value == callback.data), None)
    await state.update_data(department_name=department_name)
    await state.set_state(UserForm.group_name)
    await callback.message.answer(text=f"Хорошо, введи название своей группы")


@router.message(UserForm.group_name)
async def process_group_name(message: types.Message, state: FSMContext):
    data = await state.update_data(group_name=message.text)
    user = SUser(
        id=message.from_user.id,
        name=data.get("name"),
        group_name=data.get("group_name"),
        department_name=data.get("department_name"),
    )
    await UsersService.create_user(user)
    await state.clear()
    text = f"Пользователь создан, теперь в расписание будут добавляться индивидуальные занятия для {user.name}"
    await message.answer(text=text, reply_markup=main_kb)
