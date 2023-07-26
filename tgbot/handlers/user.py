from uuid import uuid4

from aiogram import F, Bot
from aiogram import Router
from aiogram.filters import CommandStart, Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.database.requests import log_game
from tgbot.keyboards.inline import make_newgame_keyboard, make_keyboard_with_new_word
from tgbot.keyboards.reply import make_choose_keyboard
from tgbot.misc.states import Game
from tgbot.wordle import check_word, Outcome, get_random_word5, get_stats, get_random_word6, get_unused_letters

user_router = Router()


async def user_log_game(message: Message, state: FSMContext, session_pool, data: dict, win: bool):
    await state.update_data({"game_id": str(uuid4())})
    await log_game(session_pool, data, message.from_user.id, win)


async def user_new_game(message: Message, state: FSMContext, word_length: int, offset: int):
    msg_id = message.message_id
    await state.set_state(Game.attempt.state)
    await state.set_data(data={"attempt": 1, "used_words": [],
                               "message_id": msg_id + offset, "word_length": word_length})
    if word_length == 5:
        random_word = get_random_word5()
        await state.update_data({"answer": random_word})
    if word_length == 6:
        random_word = get_random_word6()
        await state.update_data({"answer": random_word})
    await message.answer("Угадайте слово.", reply_markup=make_newgame_keyboard(word_length))


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Это игра Вордли!\n"
                         "Как играть: https://telegra.ph/Pravila-igry-Vordli-05-20\n"
                         "Выбери режим:",
                         disable_web_page_preview=True, reply_markup=make_choose_keyboard())


@user_router.message(Text(text=["5 букв", "6 букв [hard]"]))
async def user_choose_letters(message: Message, state: FSMContext):
    if message.text == "5 букв":
        word_length = 5
        await user_new_game(message, state, word_length, 1)
        await state.update_data({"message_id": message.message_id + 1})
    elif message.text == "6 букв [hard]":
        word_length = 6
        await message.answer("Вы выбрали сложный режим. В нашей базе около 14.000 шестибуквенных слов. "
                             "Вам может загадаться <b>любое</b> из них")
        await user_new_game(message, state, word_length, 2)
        await state.update_data({"message_id": message.message_id + 2})


@user_router.message(Command("help"))
async def user_help(message: Message):
    await message.answer("Привет! Это игра Вордли.\n"
                         "Для просмотра своей статистики пиши /stats\n"
                         "Как играть: https://telegra.ph/Pravila-igry-Vordli-05-20",
                         disable_web_page_preview=True)


@user_router.message(Command("settings"))
async def user_settings(message: Message):
    await message.answer("Выберите длину слова.", reply_markup=make_choose_keyboard())


@user_router.callback_query(Text("0"))
async def user_click_letter(callback: CallbackQuery):
    await callback.answer()


@user_router.message(Command("stats"))
async def user_stats(message: Message, session_pool):
    stats = await get_stats(session_pool, message.from_user.id)
    await message.answer(stats)


@user_router.message(F.text, Game.attempt)
async def user_attempt(message: Message, bot: Bot, state: FSMContext, session_pool):
    data = await state.get_data()
    word = message.text.lower()
    check = check_word(word=word, used_words=data["used_words"], answer=data["answer"], word_length=data["word_length"])

    if check == Outcome.length_error:
        await message.answer(f"Длина слова должна быть {data['word_length']}.")
        return

    if check == Outcome.exists_error:
        await message.answer("Этого слова не существует.")
        return

    if check == Outcome.already_used_error:
        await message.answer("Вы уже использовали это слово.")
        return

    data["used_words"].append(word)
    used_words = data["used_words"]
    answer = data["answer"]

    if check == Outcome.wrong:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data["message_id"],
                                    text="Неиспользованные буквы: " + get_unused_letters(used_words))
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["message_id"],
                                            reply_markup=make_keyboard_with_new_word(answer=answer,
                                                                                     used_words=used_words,
                                                                                     word_length=data["word_length"]))
        current_attempt = data["attempt"] + 1
        if current_attempt > 6:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=data["message_id"],
                                        text=f"Проигрыш :(\nОтвет был: {data['answer']}")
            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["message_id"],
                                                reply_markup=make_keyboard_with_new_word(answer=answer,
                                                                                         used_words=used_words,
                                                                                         word_length=data["word_length"]))
            # Log game.
            await user_log_game(message, state, session_pool, data, False)
            # New game.
            await user_new_game(message, state, word_length=data["word_length"], offset=1)
            return
        else:
            await state.update_data({"attempt": current_attempt, "used_words": used_words})

    if check == Outcome.win:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data["message_id"],
                                    text="<b>Победа!</b>")
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["message_id"],
                                            reply_markup=make_keyboard_with_new_word(answer=answer,
                                                                                     used_words=used_words,
                                                                                     word_length=data["word_length"]))
        if data["attempt"] == 1:
            await message.answer_photo(
                "AgACAgIAAxkBAAICHWRj10iHat3GbO3LmrGu6gyoUzbZAAKExjEbRsAhS4jsHxndpcQQAQADAgADeQADLwQ",
                caption="Везение уровня бог!")
            await user_log_game(message, state, session_pool, data, True)
            await user_new_game(message, state, word_length=data["word_length"], offset=2)
            return

        await user_log_game(message, state, session_pool, data, True)
        await user_new_game(message, state, word_length=data["word_length"], offset=1)
