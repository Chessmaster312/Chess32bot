from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

import bootstrap
from settings import config

cancel_btn = [[InlineKeyboardButton(text='❌Отмена', callback_data="delete")]]
close_room_btn = lambda room_id: [[InlineKeyboardButton(text='Закрыть комнату', callback_data=f"close_room_{room_id}")]]
exit_btn = [[InlineKeyboardButton(text='🚪Выйти из игры', callback_data="exit")]]
share_btn = lambda session_id: [[InlineKeyboardButton(text=f'🔗Поделиться ссылкой на игру',url=f'https://t.me/share/url?url=https://t.me/YOUR_BOT?start={session_id}&text=Сыграй со мной!')]]
kbd = lambda buttons: InlineKeyboardMarkup(inline_keyboard=buttons)

bot = bootstrap.MyBot().getInstance()

async def webapp(session_id, site):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🕹Войти в игру', web_app=WebAppInfo(url=f"https://{config.DOMEN}/{session_id}/{site}"))]])

async def remove_job(job_id, scheduler):
    try:
        scheduler.get_job(job_id).remove()
    except:
        pass


async def sending_users(users: list[str|int], text: str, markup: InlineKeyboardMarkup):
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id,
                                   text=text,
                                   reply_markup=markup)
        except:
            continue
