from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import config
from yookassa_pay import Payed


async def send_message(message):
    await message.answer("Скоро у вас появится возможность приобрести подписку")
    return
    #payment = Payed(config.premium, message)
    #await payment.create()
    #print(payment.url, flush=True)
    #keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #    [InlineKeyboardButton(text='Оплатить', url=payment.url)]])
    #await message.answer("Ссылка на оплату",reply_markup=keyboard)
