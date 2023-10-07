from datetime import datetime

from aiogram import types
from aiogram.filters import CommandObject
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import bootstrap
from handlers import game_controller
from settings import config

db = bootstrap.DB().getInstance()

db = bootstrap.DB().getInstance()
bot = bootstrap.MyBot().getInstance()
STATS_BUTTON_TEXT = '⭐Рейтинг'
LINK_BUTTON_TEXT = '💬Чат игроков шахматного бота'
MY_STATS_BUTTON_TEXT = '📈Моя статистика'
PREMIUM_BUTTON_TEXT = '💳Оформить подписку'
REF_BUTTON_TEXT = '🔗Реферальная система'
GAME_BUTTON_TEXT = '🕹️Играть'
ADMIN_PANEL_TEXT = '⌨Админ панель'
INFO_PANEL_TEXT = '⌨Инструкция'



async def send_keyboard(message: types.Message):
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message
    buttons = [[KeyboardButton(text=GAME_BUTTON_TEXT)],
                  [KeyboardButton(text=STATS_BUTTON_TEXT), KeyboardButton(text=PREMIUM_BUTTON_TEXT)],
                  [KeyboardButton(text=REF_BUTTON_TEXT), KeyboardButton(text=INFO_PANEL_TEXT)],
                [KeyboardButton(text=MY_STATS_BUTTON_TEXT)]]
    if message.from_user.id in [i[0] for i in config.admins_list]:
        buttons.append([KeyboardButton(text=ADMIN_PANEL_TEXT)])
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    await message.answer("Привет! Выбери пункт меню", reply_markup=keyboard)

async def start(message: types.Message, command: CommandObject):
    args = command.args
    if args and args.startswith('REF_'):
        user = await db.get_user(str(message.from_user.id))
        if user.get('reffer_id'):
            await send_keyboard(message)
            return
        await db.add_user(str(message.from_user.id), message.from_user.username or "Аноним", args.split('_')[1])
        await db.add_balance(str(message.from_user.id))
    elif args and args.startswith('utm_'):
        if args in config.utm.keys():
            config.utm.update({args: config.utm.get(args) + 1})
            setattr(config, "utm", config.utm)
    elif args:
        await game_controller.invite_friend(message, args)
        return
    await db.add_user(str(message.from_user.id), message.from_user.username or "Аноним")
    await send_keyboard(message)
    return

