from aiogram import Router, F, Bot
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from tgbot.filters.admin import AdminFilter
from tgbot.database.requests import get_bot_users, get_all_games
from tgbot.misc.states import Broadcast
from tgbot.keyboards.inline import make_sure_broadcast_keyboard
from tgbot.services.broadcaster import broadcast

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("bot"))
async def admin_bot_stats(message: Message, session_pool):
    users = await get_bot_users(session_pool)
    games = await get_all_games(session_pool)
    await message.reply(f"Пользователи: {len(users)}\nВсего игр: {len(games)}")


@admin_router.message(Command("broadcast"))
async def admin_broadcast(message: Message, state: FSMContext):
    await message.answer("Внимание! Вы собираетесь сделать рассылку <b>ВСЕМ</b> пользователям.\n"
                         "Для отмены нажмите сюда -> /cancel_broadcast\n"
                         "Введите сообщение для рассылки:\n")
    await state.set_state(Broadcast.msg.state)


@admin_router.message(Command("cancel_broadcast"))
async def admin_broadcast(message: Message, state: FSMContext):
    await message.answer("Рассылка отменена")
    await state.clear()


@admin_router.message(Broadcast.msg)
async def admin_sure_broadcast(message: Message, state: FSMContext):
    await message.answer(message.text, reply_markup=make_sure_broadcast_keyboard())
    await state.set_data({"msg": message.text})
    await state.set_state(Broadcast.sure.state)


@admin_router.callback_query(Broadcast.sure, Text("nobroadcast"))
async def no_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Рассылка отменена", reply_markup=None)
    await state.clear()


@admin_router.callback_query(Broadcast.sure, Text("yesbroadcast"))
async def run_broadcast(callback: CallbackQuery, bot: Bot, state: FSMContext, session_pool):
    await callback.answer()
    users = await get_bot_users(session_pool)
    data = await state.get_data()
    msg = data["msg"]
    await state.clear()
    await callback.message.edit_text("Рассылка начата. Ожидайте...", reply_markup=None)
    count = await broadcast(bot, users, msg)
    await callback.message.answer(f"Рассылка закончена. Отправлено сообщений: {count}")
