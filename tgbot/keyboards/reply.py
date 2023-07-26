from aiogram.utils.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder, KeyboardButton, KeyboardBuilder


def make_choose_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text="5 букв"),
                 KeyboardButton(text="6 букв [hard]"))
    return keyboard.as_markup(resize_keyboard=True)
