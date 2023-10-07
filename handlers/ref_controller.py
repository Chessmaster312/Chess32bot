import bootstrap

db = bootstrap.DB().getInstance()



async def send_message(message):
    data = await db.get_user(str(message.from_user.id)) or {}
    count = await db.count_ref(str(message.from_user.id))
    #await message.answer(f"Реферальная система дает вам возможность, участвовать в еженедельных розыгрышах денежных призов от 3000р-10000р.\n\nДля того чтобы принять участие вам достаточно в неделю приглашать 2х друзей и вы автоматически становитесь участником розыгрыша.\nПризовых мест 10!\n\nДля получения приза вам нужно связаться с менеджером, указанным в шапке профиля\n\n*Количество рефералов*: {count or 'Нет данных'}\n*Количество баллов*: {data.get('balance','Нет данных')}\n\n*Ваша реферальная ссылка*(нажмите, чтобы скопировать):\n`https://t.me/ChatLabs_Test_Bot?start=REF_{message.from_user.id}`", parse_mode="markdown")
    await message.answer(f"*Количество рефералов*: {count or 'Нет данных'}\n*Количество баллов*: {data.get('balance','Нет данных')}\n\n*Ваша реферальная ссылка*(нажмите, чтобы скопировать):\n`https://t.me/Chess32bot?start=REF_{message.from_user.id}`", parse_mode="markdown")
