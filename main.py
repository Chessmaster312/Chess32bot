import asyncio
import datetime
import logging
import os

import aiohttp
import aiohttp_jinja2
import jinja2
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeDefault
from aiohttp import web
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import bootstrap
import router
import routes
from db_api import create_table
from db_api.postgresql import Database
from handlers.stats_controller import send_priz_message
from websocket import wsManager
from engine import SessionManager

app = web.Application(client_max_size=1024 ** 3)
app.add_routes([web.static('/img', os.path.join(os.getcwd(), "img"))])
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
async def close_sessions():
    for session in aiohttp.ClientSession._instances:
        await session.close()

async def main():
    bootstrap.bootstrap()
    db = bootstrap.DB().getInstance()
    scheduler = bootstrap.Scheduler().getInstance()
    await db.create_pool()
    print(db.pool)
    #db.casino.support_queue.delete_many({})
    await create_table.run()
    bot = bootstrap.MyBot().getInstance()
    dp = bootstrap.MyDispatcher().getInstance()
    scheduler.configure()
    scheduler.add_job(SessionManager.search, IntervalTrigger(seconds=1))

    router.register_commands()
    scheduler.start()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "build")))
    app.router.add_get('/{game_id}/{side}', routes.index)
    app.router.add_post('/get_opponent', routes.get_opponent)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    await wsManager.start_server()
    await dp.start_polling(bot)
    await bot.delete_my_commands(BotCommandScopeDefault())
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass

    await close_sessions()

if __name__ == '__main__':
    asyncio.run(main())
