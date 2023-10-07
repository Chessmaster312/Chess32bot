from typing import Callable, Any, Awaitable, Dict

from aiogram import types
from aiogram.dispatcher.middlewares import base
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

import bootstrap
from settings import config
bot = bootstrap.MyBot().getInstance()
dp = bootstrap.MyDispatcher().getInstance()
async def check(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=config.channel, user_id=user_id)
        return chat_member.status in ("member", "creator", "administrator")
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

async def kbd():
    try:
        link = await bot.get_chat(config.channel)
        link = link.invite_link
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Подписаться!',url=link)],
                                                     [InlineKeyboardButton(text='Я подписался!', callback_data="start")]])
    except Exception as e:
        print("fdsfFSSDFKHSJKDFHSKFD", e, flush=True)
        pass


class CheckSubscriptionMiddleware(base.BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        message = event
        user_id = message.from_user.id
        if isinstance(event, CallbackQuery):
            message = event.message
            user_id = message.chat.id
        if message.text == "/start":
            return await handler(event, data)
        print(user_id)
        await dp.fsm.storage.set_data(bot, user_id, message)
        if user_id in [i[0] for i in config.admins_list]:
            return await handler(event, data)
        if not await check(user_id):
            await message.answer("Для продолжения работы с ботом, пожалуйста, подпишитесь на наш канал.", reply_markup=await kbd())
            return False
        return await handler(event, data)


