from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard = [
        [
            KeyboardButton(text = "/login"),
            KeyboardButton(text = "/Расписание"),
        ],
    ]
    )

admin_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="/Создать "
                                "сбор"),
            KeyboardButton(text="/Подтвердить")
        ],
        [
            KeyboardButton(text="назад")
        ]
    ]
)