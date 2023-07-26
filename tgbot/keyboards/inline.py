from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.wordle.wordle import get_emoji_word


def make_newgame_keyboard(word_length) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    row = [InlineKeyboardButton(text="❔", callback_data="0") for _ in range(word_length)]
    for _ in range(6):
        keyboard.row(*row)
    return keyboard.as_markup()


def make_sure_broadcast_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Да", callback_data="yesbroadcast"),
                 InlineKeyboardButton(text="Нет", callback_data="nobroadcast"))
    return keyboard.as_markup()


def make_keyboard_with_new_word(answer: str, used_words: list[str], word_length) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for word in used_words:
        row = [InlineKeyboardButton(text=i, callback_data="0") for i in get_emoji_word(word=word, answer=answer)]
        keyboard.row(*row)
    if len(used_words) < 6:
        for _ in range(6-len(used_words)):
            row = [InlineKeyboardButton(text="❔", callback_data="0") for _ in range(word_length)]
            keyboard.row(*row)
    return keyboard.as_markup()
