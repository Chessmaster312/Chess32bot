
import json

import asyncio
import uuid

import requests
from apscheduler.triggers.interval import IntervalTrigger
from yookassa import Configuration, Payment

import bootstrap
from settings import config

Configuration.account_id = config.yookassa_id
Configuration.secret_key = config.yookassa_api
db = bootstrap.DB().getInstance()
scheduler = bootstrap.Scheduler().getInstance()

payments = {}

## from utils.db_api.qiwi import add_payment
# wallet = pyqiwi.Wallet(token=QIWI_TOKEN, number=WALLET_QIWI)
# from pyqiwi import generate_form_link


class NotEnoughMoney:
    pass


class NoPaymentFound(Exception):
    pass


class Payed:
    _instances = {}

    def __new__(cls, amount, message):
        if message.from_user.id not in cls._instances:
            cls._instances[message.from_user.id] = super(Payed, cls).__new__(cls)
        return cls._instances[message.from_user.id]

    def __init__(self, amount, message):
        if not hasattr(self, "initialized"):
            self.payment = None
            self.message = message
            self.url = None
            self.id = None
            self.amount = amount
            self.initialized = True

    async def create(self):
        if not self.url:
            idempotence_key = str(uuid.uuid4())
            payment = Payment.create({
                "amount": {
                    "value": self.amount,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "capture": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://www.example.com/return_url"
                },
            }, idempotence_key)
            payment_data = json.loads(payment.json())
            self.id = payment.id
            self.url = payment.confirmation.confirmation_url
            job = scheduler.add_job(self.start_check, IntervalTrigger(seconds=5), id=self.id)


    async def start_check(self):
        self.payment = Payment.find_one(self.id)
        match str(self.payment.status):
            case "pending":
                return
            case "canceled" | "failed":
                scheduler.remove_job(self.id)
                self.url = None
            case "succeeded":
                scheduler.remove_job(self.id)
                self.url = None
                await db.add_premium(str(self.message.from_user.id))
                await self.message.answer("Вы успешно оплатили подписку!")
            case _:
                scheduler.remove_job(self.id)
                self.url = None
                return self.id

    @property
    def link(self):
        return self.url
