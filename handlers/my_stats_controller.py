from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import bootstrap
from settings import config
db = bootstrap.DB().getInstance()


async def send_game_history_message(message):
    games = await db.get_last_10_games(str(message.from_user.id))
    if games:
        text = []
        for i, game in enumerate(games, start=1):
            date = game['date']
            side = game['side']
            history = game['history']
            text.append(f"{i}. *дата*: {date}, *сторона*: {side}\n*история ходов*:\n{history or 'Нет данных'}")
        text = "\n".join(text)
        print(text, flush=True)
    else:
        text = "🛑Нет данных, сыграйте партию, чтобы получить историю ходов"
    await message.message.answer(f"История последних 10 игр:\n\n{text}", parse_mode = "markdown")
    await message.answer()

async def send_message(message):
    if not await db.check_premium(str(message.from_user.id)):
        await message.answer("У вас нет подписки, оформите!")
        return
    result = await db.get_user(str(message.from_user.id))
    users_text = f'*Рейтинг ELO*: {result.get("elo", "Нет данных")}\n\n'\
                 f'*Винрейт*: {result.get("winrate", "Нет данных")}%\n\n'\
                 f'*Дата истечения подписки*: {result.get("premium_time", "Нет данных")}'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👩‍🏫Разбор партии', url=config.link_help_game)],
        [InlineKeyboardButton(text='📝История партий', callback_data="game_history")]])
    await message.answer(users_text, reply_markup=keyboard, parse_mode="markdown")