from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

departments_short_names = {
    "Аспирантура": "Аспирантура",
    "Гуманитарный факультет": "Гуманитарный",
    "Психолого-педагогический факультет": "Псих-пед",
    "Факультет дефектологии и естественно-научного образования": "Дефектологии",
    "Факультет дополнительных образовательных программ": "ДОП",
    "Факультет искусств и физической культуры": "Искусств",
    "Факультет среднего профессионального образования": "СПО",

}

select_department_kb = InlineKeyboardBuilder()
for full_name, short_name in departments_short_names.items():
    select_department_kb.button(text=short_name, callback_data=short_name)
select_department_kb.adjust(1)
select_department_kb = select_department_kb.as_markup()

user_exist_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard = [
        [
            KeyboardButton(text = "/Удалить"),
            KeyboardButton(text = "/Оставить"),
        ],
    ]
)