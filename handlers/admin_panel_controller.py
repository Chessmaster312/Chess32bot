import asyncio

import requests
from aiogram.fsm.context import FSMContext

import bootstrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from settings import config
from states import AdminSupportStates
from websocket import wsManager

bot = bootstrap.MyBot().getInstance()
dp = bootstrap.MyDispatcher().getInstance()
db = bootstrap.DB().getInstance()
back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data="back")]])


async def send_message(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✉Рассылка', callback_data="spam")],
        [InlineKeyboardButton(text='🤖Botstat', url='https://botstat.io/')],
        [InlineKeyboardButton(text='🔗Изменить привязанный канал', callback_data="channel")],
        [InlineKeyboardButton(text='💱Изменить сумму розыгрыша', callback_data="priz")],
        [InlineKeyboardButton(text='➕Добавить utm ссылку', callback_data="utm")],
        [InlineKeyboardButton(text='👨‍🏭Изменить аккаунт выплат', callback_data="link_get_priz")],
        [InlineKeyboardButton(text='👨‍💼Изменить администраторов бота', callback_data="admins_list")],
        [InlineKeyboardButton(text='ℹ️Изменить сообщение с информацией', callback_data="info")],
        [InlineKeyboardButton(text='❌Закрыть панель', callback_data="close")]])
    await message.answer(f'*Статистика игр*\n'
                         f'Количество активных игроков: {len(wsManager.connected_users)}\nВсего сыгранных игр: {await db.games_count()}\n\n'
                         f'*Статистика рефералов*\n'
                         f'Количество переходов по рефам за неделю: {await db.get_all_ref_week()}',
                         reply_markup=keyboard, parse_mode="markdown")


async def send_default(message: CallbackQuery|Message, state: FSMContext, name=None):
    if isinstance(message, CallbackQuery):
        answer_message=message.message
    else:
        answer_message = message
    match name or message.data:
        case "channel":
            await state.set_state(AdminSupportStates.channel)
            msg = await answer_message.answer(
                f'Отправьте новое значение в виде айди канала(важно, чтобы бот был добавлен администратором)\n'
                f'Текущее значение: {config.channel}', reply_markup=back)
            await state.set_data({"new_message":msg})
        case "priz":
            await state.set_state(AdminSupportStates.priz)
            msg = await answer_message.answer(
                f'Отправьте новое значение\n'
                f'Текущее значение: {config.priz}', reply_markup=back)
            await state.set_data({"new_message": msg})
        case "link_get_priz":
            await state.set_state(AdminSupportStates.link_get_priz)
            msg = await answer_message.answer(
                f'Отправьте новую ссылку на аккаунт\n'
                f'Текущее значение: {config.link_get_priz}', reply_markup=back)
            await state.set_data({"new_message": msg})
        case "admins_list":
            msg = await send_staff_list(answer_message, state)
            await state.set_data({"new_message": msg})
        case "spam":
            await state.set_state(AdminSupportStates.Spam_Input)
            await answer_message.answer('Отпрвьте сообщение, которое я смогу разослать')
        case "utm":
            await state.set_state(AdminSupportStates.utm)
            text=''
            for i, (k, v) in enumerate(config.utm.items()):
                text += f"*№{i}*:\n"+f"*Ссылка*:`https://t.me/Chess32bot?start={k}`\n"+f"*Переходы*:{v}\n\n"
            msg = await answer_message.answer(f"Оправьте номер ссылки, чтобы удалить ее или отправьте название, чтобы добавить\n\n{text or 'Нет данных'}", reply_markup=back, parse_mode="markdown")
            await state.set_data({"new_message": msg})
        case "info":
            await state.set_state(AdminSupportStates.info)
            msg = await answer_message.answer(
                f'Отправьте новое значение\n\n'
                f'Текущее значение: {config.info}', reply_markup=back)
            await state.set_data({"new_message": msg})
        case "back":
            await send_message(answer_message)
            await state.clear()
    msg = await dp.fsm.storage.get_data(bot, answer_message.chat.id)
    await msg.delete()
    await message.answer()


async def edit_default(message: Message, state: FSMContext):
    current_state = await state.get_state()
    attr = str(current_state).split(":")[1]
    if attr == "link_get_priz":
        request = requests.get(message.text)
        if request.status_code != 200:
            await message.answer('Невалидный адрес')
            return
    elif attr == "utm":
        if message.text.isdigit():
            config.utm.pop(list(config.utm.keys())[int(message.text)], None)
        else:
            config.utm.update({f"utm_{message.text}": 0})
        setattr(config, "utm", config.utm)
    elif attr == "admins_list":
        data = message.forward_from
        if data is None:
            await message.answer('Запрещено настройками приватности аккаунта')
            return
        user_id = data.id
        username = data.username or data.first_name or "Без имени аккаунта"
        # Проверяем наличие пользователя в списке администраторов
        if any(user_id == item[0] for item in config.admins_list):
            await message.answer("Пользователь уже является администратором.")
            return
        config.admins_list.append([user_id, username])
    elif attr == 'Spam_Input':
        users = await db.get_users()
        await message.answer('Подождите, идет рассылка')
        count = 0
        for user in users:
            try:
                await bot.copy_message(user[0], message.chat.id, message.message_id)
                await asyncio.sleep(1)
                count += 1
            except:
                continue
        await message.answer(f'Рассылка завершена, чатов затронуто: {count}')
        await state.clear()
        await send_message(message)
        return
    else:
        setattr(config, attr, message.text)
    old_message = await state.get_data()
    await old_message.get("new_message").delete()
    await state.clear()
    await send_default(message, state, attr)
    await message.delete()


async def send_staff_list(message, state):
    await state.set_state(AdminSupportStates.admins_list)
    buttons = [[InlineKeyboardButton(text=staff[1], url=f'tg://openmessage?user_id={staff[0]}'),
                InlineKeyboardButton(text="✖️", callback_data=str(i))] for i, staff in
               enumerate(config.admins_list)]
    buttons.append(back.inline_keyboard[0])
    kbd = InlineKeyboardMarkup(
        inline_keyboard=buttons)

    await message.answer(
        'Перешлите сообщение от аккаунта, который собираетесь добавить', reply_markup=kbd)


async def delete_staff(message: CallbackQuery, state: FSMContext):
    config.admins_list.pop(int(message.data))
    await message.message.delete()
    return await send_staff_list(message, state)
