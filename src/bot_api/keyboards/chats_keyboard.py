from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Create buttons
button1 = InlineKeyboardButton(text="Добавить в рассылку", callback_data="add")
button2 = InlineKeyboardButton(text="Удалить из рассылки", callback_data="delete")

# Create the keyboard with the buttons
chats_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
