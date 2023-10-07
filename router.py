import asyncio
import re

from aiogram import F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_MEMBER

import middlewares
from bootstrap import MyDispatcher

import handlers
from handlers import stats_controller, ref_controller, payment_controller, game_controller, my_stats_controller, admin_panel_controller
from settings import config
from states import AdminSupportStates


def register_commands():
    dp = MyDispatcher().getInstance()
    dp.callback_query.register(handlers.send_keyboard, F.data == 'start', state=None)
    dp.message.register(handlers.start, Command(commands='start'), state=None)
    dp.message.register(my_stats_controller.send_message, F.text == handlers.MY_STATS_BUTTON_TEXT, state=None)
    dp.message.register(lambda message: message.answer("Ссылка на чат-> "+ config.link), F.text == handlers.LINK_BUTTON_TEXT, state=None)
    dp.message.register(lambda message: message.answer(config.info), F.text == handlers.INFO_PANEL_TEXT, state=None)
    dp.message.register(ref_controller.send_message, F.text == handlers.REF_BUTTON_TEXT,state=None)
    dp.message.register(game_controller.send_keyboard, F.text == handlers.GAME_BUTTON_TEXT,state=None)
    dp.message.register(payment_controller.send_message, F.text == handlers.PREMIUM_BUTTON_TEXT,state=None)
    dp.message.register(admin_panel_controller.send_message, F.text == handlers.ADMIN_PANEL_TEXT,state=None)
    dp.message.register(stats_controller.send_message, F.text == handlers.STATS_BUTTON_TEXT,state=None)
    dp.callback_query.register(game_controller.send_with_friend, F.data == 'with_friend',state=None)
    dp.callback_query.register(game_controller.random_search, F.data == 'random',state=None)
    dp.callback_query.register(game_controller.delete, F.data == 'delete',state=None)
    dp.callback_query.register(game_controller.close_room, F.data.regexp(r"^close_room"),state=None)
    dp.callback_query.register(admin_panel_controller.send_default, F.data.regexp(r"^(channel|priz|link_get_priz|admins_list|spam|back|info|utm)$"),state="*")
    dp.message.register(admin_panel_controller.edit_default, state=AdminSupportStates)
    dp.callback_query.register(my_stats_controller.send_game_history_message, F.data == 'game_history',state=None)
    dp.callback_query.register(admin_panel_controller.delete_staff, F.data.isdigit(),state=AdminSupportStates.admins_list)
    dp.callback_query.register(lambda callback: callback.message.delete(), F.data == 'close',state=None)
    dp.callback_query.register(game_controller.exit, F.data == 'exit',state=None)


