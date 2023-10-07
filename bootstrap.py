import asyncio

import pymongo
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import config
from db_api.postgresql import Database

class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DB(metaclass=MetaSingleton):
    connection = None

    def getInstance(self):
        if self.connection is None:
            self.connection = Database(config.dsn)
        return self.connection


class MyBot(metaclass=MetaSingleton):
    instance = None

    def getInstance(self):
        if self.instance is None:
            self.instance = Bot(token=config.token, parse_mode="HTML")
        return self.instance

class Scheduler(metaclass=MetaSingleton):
    instance = None

    def getInstance(self):
        if self.instance is None:
            self.instance = AsyncIOScheduler()

        return self.instance


class MyDispatcher(metaclass=MetaSingleton):
    instance = None

    def getInstance(self):
        if self.instance is None:
            self.instance = Dispatcher(storage=MemoryStorage())
        return self.instance


def bootstrap():
    DB()
    MyBot()
    MyDispatcher()
    Scheduler()
