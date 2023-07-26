from aiogram.fsm.state import State, StatesGroup


class Game(StatesGroup):
    attempt = State()


class Broadcast(StatesGroup):
    msg = State()
    sure = State()
