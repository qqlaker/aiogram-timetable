from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_keyboard_row(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
