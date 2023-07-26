from aiogram import types, Router, F

echo_router = Router()


@echo_router.message(F.text)
async def bot_echo_all(message: types.Message):
    await message.answer("Извините, я не знаю такой команды.")
