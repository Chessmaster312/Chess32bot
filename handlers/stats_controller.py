import bootstrap
from settings import config

bot = bootstrap.MyBot().getInstance()
db = bootstrap.DB().getInstance()


async def send_message(message):
    result = await db.get_top_10_active_users()
    if result:
        users_list = []
        for i, user in enumerate(result, 1):
            winrate = user['winrate']
            prize = int(config.priz)/i # Формула для вычисления выигрыша
            user_info = f"{i}. *{user['username']}* ({winrate}% побед) выигрыш: {prize}₽"
            users_list.append(user_info)
        users_text = "\n".join(users_list)
    else:
        users_text = "🛑Нет данных"
    #await message.answer(f"Рейтинг рассчитывается исходя из вашего общего % выигрышей и проигрышей, чем он выше тем выше шанс выиграть денежный приз.\n\nОн будет для наглядности публиковаться еженедельно\n\nРейтинг активных игроков:\n\n{users_text}", parse_mode = "markdown")
    await message.answer(f"Рейтинг активных игроков:\n\n{users_text}", parse_mode = "markdown")

async def send_priz_message():
    result = await db.get_top_10_active_users()
    if result:
        for i, user in enumerate(result, 1):
            prize = config.priz/i # Формула для вычисления выигрыша
            try:
                await bot.send_message(user['id'], f"Вы выиграли:{prize}\n\nНапишите сюда, чтобы забрать выигрыш: {config.link_get_priz}")
            except:
                continue