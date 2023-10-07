from datetime import datetime, timedelta
from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, CallbackQuery, Message
from apscheduler.triggers.date import DateTrigger

import bootstrap
from utils import kbd, cancel_btn, exit_btn, share_btn, close_room_btn, remove_job
from engine import SessionManager
from websocket import wsManager

bot = bootstrap.MyBot().getInstance()
scheduler = bootstrap.Scheduler().getInstance()


async def checker(event: Union[Message, CallbackQuery]):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
        await message.edit_text(text=message.text, reply_markup=None)

    user_id = str(message.chat.id)
    if await SessionManager.check_exist(user_id):
        await message.answer("У вас уже начата игра. Играйте, либо сдайтесь", reply_markup=kbd(exit_btn))
        return True
    if user_id in SessionManager.user_search:
        await message.answer("Вы уже в поиске", reply_markup=kbd(cancel_btn))
        return True


async def send_keyboard(message: Message):
    if await checker(message):
        return
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔀Случайный соперник', callback_data="random"),
             InlineKeyboardButton(text='🤼Сыграть с другом', callback_data="with_friend")]])
        await message.answer("Чтобы начать игру выберите режим", reply_markup=keyboard)


async def send_with_friend(callback: CallbackQuery):
    if await checker(callback):
        return
    user_id = str(callback.message.chat.id)
    room_id = await SessionManager.create_room()
    await SessionManager.add_user_room(room_id, user_id)
    time = datetime.now() + timedelta(minutes=5)
    scheduler.add_job(lambda: close_room(callback, room_id=room_id),
                      DateTrigger(run_date=time))
    btns = share_btn(room_id)
    btns.extend(close_room_btn(room_id))
    await bot.send_message(callback.from_user.id,
                           'Поделитесь ссылкой на комнату с другом и войдите в игру, чтобы сыграть партию',
                           reply_markup=kbd(btns))
    await callback.answer()


async def close_room(callback: CallbackQuery, room_id = None):
    if not room_id:
        room_id = callback.data.split("_")[-1]
    SessionManager.rooms.pop(room_id, None)
    try:
        await callback.message.delete()
    except:
        pass

async def invite_friend(message: Message, args):
    if await checker(message):
        return
    user_id = str(message.chat.id)
    print(args, SessionManager.rooms, flush=True)
    if args in SessionManager.rooms:
        await SessionManager.add_user_room(args, user_id)
    else:
        await message.answer('Игра не найдена')


async def random_search(callback: CallbackQuery):
    user_id = str(callback.message.chat.id)
    if await checker(callback):
        return

    SessionManager.user_search.update({user_id})
    msg = await bot.send_message(user_id, 'Идет поиск игры...', reply_markup=kbd(cancel_btn))
    time = datetime.now() + timedelta(minutes=5)
    scheduler.add_job(delete, DateTrigger(run_date=time), args=[msg], id=f"SEARCH{user_id}")
    await callback.answer()


async def delete(event: Union[Message, CallbackQuery]):
    try:
        if isinstance(event, Message):
            message = event
            user_id = str(message.chat.id)
            await message.answer("Сейчас никто не хочет играть, попробуйте позже")
            await message.delete()

        else:
            callback = event
            user_id = str(callback.message.chat.id)
            await callback.message.delete()
            await remove_job(f"SEARCH{user_id}", scheduler)
        SessionManager.user_search.remove(user_id)
        print(SessionManager.user_search)
    except Exception as e:
        print(e)
        pass


async def exit(message: Union[Message, CallbackQuery]):
    if isinstance(message, CallbackQuery):
        message = message.message
    try:
        game = await SessionManager.close(wsManager=wsManager, user_id=message.chat.id)
        await game.disconnected(message.chat.id)
    except:
        pass
    await message.delete()
