import os
import json
import random
from string import Template
from collections import Counter

from tgbot.database.requests import get_games_by_id
from tgbot.database.models import GameHistoryEntry

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "answers5.json"), "r", encoding="utf-8") as f:
    answers5 = json.load(f)

with open(os.path.join(base_dir, "words5.json"), "r", encoding="utf-8") as f:
    words5 = json.load(f)

with open(os.path.join(base_dir, "answers6.json"), "r", encoding="utf-8") as f:
    answers6 = json.load(f)

with open(os.path.join(base_dir, "words6.json"), "r", encoding="utf-8") as f:
    words6 = json.load(f)


class Outcome:
    already_used_error: int = 1
    length_error: int = 2
    exists_error: int = 3
    wrong: int = 4
    win: int = 5


def check_word(word: str, used_words: list, answer: str, word_length: int):
    if "ё" in word:
        word = word.replace("ё", "е")
    if len(word) != word_length:
        return Outcome.length_error
    if word in used_words:
        return Outcome.already_used_error
    if word_length == 5:
        if word not in words5:
            return Outcome.exists_error
    if word_length == 6:
        if word not in words6:
            return Outcome.exists_error
    if word != answer:
        return Outcome.wrong
    if word == answer:
        return Outcome.win


def get_unused_letters(words: list[str]):
    letters = set(chr(x) for x in range(1072, 1104))
    words_letters = set("".join(words))
    return " ".join(list(letters - words_letters)).title()


def get_random_word5() -> str:
    return answers5[random.randint(1, len(answers5))]


def get_random_word6() -> str:
    return answers6[random.randint(1, len(answers6))]


def get_emoji_word(word: str, answer: str) -> list[str]:
    word = word.upper()
    answer = answer.upper()
    result = list()

    letters_answer = Counter(answer)
    colored_letters = dict()
    for letter in word:
        colored_letters[letter] = 0

    for index, letter in enumerate(word):
        if word[index] == answer[index]:
            result.append("🟢"+letter)
            colored_letters[letter] += 1
        else:
            result.append(letter)

    for index, letter in enumerate(word):
        if word[index] == answer[index]:
            continue

        elif (letter in answer) and (colored_letters[letter] < letters_answer[letter]):
            result[index] = "🟠" + letter
            colored_letters[letter] += 1

    return result


async def get_stats(session_pool, user_id: int):
    games = await get_games_by_id(session_pool, user_id)

    if len(games) == 0:
        return "У Вас пока нет статистики. Нажмите /start и начинайте играть!"

    game: GameHistoryEntry
    template = Template("""
📊 <u>Ваша персональная статистика</u>:

Всего игр сыграно: <b>$games_count</b>
В среднем попыток на угаданное слово: <b>$average_attempts</b>

🟢 <b>Пятибуквенные</b> слова:
Игр: <b>$games_count5</b>. Побед: <b>$wins5</b> (<b>$percent5</b>%)

🟢 <b>Шестибуквенные</b> слова:
Игр: <b>$games_count6</b>. Побед: <b>$wins6</b> (<b>$percent6</b>%)
""")
    games5 = [game for game in games if game.length == 5]
    games6 = [game for game in games if game.length == 6]
    wins5, wins6 = 0, 0
    percent5, percent6 = 0, 0
    total_attempts_victory = 0

    if len(games5) != 0:
        for game in games5:
            wins5 += game.victory
            if game.victory:
                total_attempts_victory += game.attempts
        percent5 = int(round(wins5 / len(games5) * 100, 0))

    if len(games6) != 0:
        for game in games6:
            wins6 += game.victory
            if game.victory:
                total_attempts_victory += game.attempts
        percent6 = int(round(wins6 / len(games6) * 100, 0))

    if wins5 + wins6 != 0:
        average_attempts = float("{:.1f}".format(total_attempts_victory / (wins5 + wins6)))
    else:
        average_attempts = 0

    return template.substitute(games_count5=len(games5), average_attempts=average_attempts, wins5=wins5, wins6=wins6,
                               percent5=percent5, games_count6=len(games6), percent6=percent6, games_count=len(games))
