import os

from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from app.settings import config, translations


async def send_post(post, user_id, bot, keyboard=None):
    file_extension = os.path.splitext(post.get("path"))[1].lower()

    if file_extension in (".png", ".jpg", ".jpeg"):
        await bot.send_photo(user_id, photo=FSInputFile(os.path.join(os.getcwd(), 'media', post.get("path"))),
                             caption=post.get("text"), reply_markup=keyboard)
    elif file_extension in (".gif"):
        await bot.send_animation(user_id,
                                 animation=FSInputFile(os.path.join(os.getcwd(), 'media', post.get("path"))),
                                 caption=post.get("text"), reply_markup=keyboard)
    elif file_extension in (".mp4"):
        await bot.send_video(user_id, video=FSInputFile(os.path.join(os.getcwd(), 'media', post.get("path"))),
                             caption=post.get("text"), reply_markup=keyboard)


async def send_best_post(db, bot):
    post = await db.get_best_post()
    if not post:
        return
    try:
        dislikes = post.get("dislikes") if post.get("dislikes") not in (None, 0) else ""
        likes = post.get("dislikes") if post.get("dislikes") not in (None, 0) else ""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'{likes}👍🏻', callback_data='👍🏻'),
             InlineKeyboardButton(text=f'{dislikes}👎🏻', callback_data='👎🏻')],
            [InlineKeyboardButton(text=getattr(translations, 'en').get("urltext"), callback_data='link',
                                  url=config.url)]])
        await send_post(post[0], config.channel, bot, keyboard)
    except:
        pass


async def job_notification(user_id, message, bot):
    try:
        await bot.send_message(chat_id=user_id, text=message)
    except:
        pass


async def job_subscribe_activity(db, bot):
    count = await bot.get_chat_member_count(config.channel)
    await db.insert_subscribe_activity(count)


async def job_send_timer_post(post, db, bot):
    user_ids = await db.get_users()
    for user_id in user_ids:
        try:
            await send_post(post, user_id.get('id'), bot)
        except Exception as e:
            print(e)
            pass
