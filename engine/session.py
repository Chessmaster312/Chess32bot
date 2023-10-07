import random
import uuid

import bootstrap
from engine.game import Game
from engine.user import User
from utils import webapp, remove_job, sending_users

db = bootstrap.DB().getInstance()
bot = bootstrap.MyBot().getInstance()
scheduler = bootstrap.Scheduler().getInstance()


class ChessGameSession(metaclass=bootstrap.MetaSingleton):
    sessions: dict[str, Game] = {}
    user_sessions: dict[str, str] = {}
    user_search: set[str] = set()
    rooms: dict[str, set] = {}

    async def search(self):
        if len(self.user_search) < 2:
            return
        users = random.sample(self.user_search, 2)
        if all(users):
            [self.user_search.remove(user) for user in users]
            session_id, game = self.create_session()
            await self.add_user(session_id, users)
            for site, user_id in {"w": users[0], "b": users[1]}.items():
                await remove_job(f"SEARCH{user_id}", scheduler)
                await sending_users([user_id],
                                    text="Игра найдена!",
                                    markup=await webapp(session_id, site))

    async def create_room(self):
        room_id = str(uuid.uuid4())[:4]
        self.rooms.update({room_id: set()})
        return room_id

    async def add_user_room(self, room_id: str, user_id: str):
        users = self.rooms.get(room_id)
        if users is None:
            return None
        users.add(user_id)
        if len(users) < 2:
            self.rooms.update({room_id: users})
        else:
            users = list(users)
            self.rooms.pop(room_id)
            session_id, game = self.create_session()
            await self.add_user(session_id, users)
            for site, user_id in {"w": users[0], "b": users[1]}.items():
                await sending_users([user_id], text="Ваш друг уже ждет вас!", markup=await webapp(session_id, site))

    def create_session(self):
        session_id = str(uuid.uuid4())
        game = Game(SessionManager=self, session_id=session_id)
        scheduler.add_job(game.timer, 'interval', seconds=1, id=f"UPDATER{session_id}")
        self.sessions.update({session_id: game})
        return session_id, game

    async def add_user(self, session_id: str, users_ids: list):
        game = self.game(session_id)
        users = [await db.get_user(user) for user in users_ids]
        users = [User(elo=user.get('elo'),
                      user_id=user.get('id'),
                      username=user.get('username'),
                      premium=user.get('premium'))
                 if user else None
                 for user in users]
        game.w, game.b = users
        self.user_sessions.update({user_id: session_id for user_id in users_ids if user_id is not None})

    def game(self, session_id: str):
        return self.sessions.get(session_id, {})

    async def check_exist(self, user_id: str):
        return user_id in self.user_sessions

    async def close(self, wsManager, session_id: str = None, user_id: str = None):
        if not session_id:
            if user_id:
                session_id = self.user_sessions.pop(str(user_id), [])
                if not session_id:
                    return
            else:
                return
        await remove_job(f"UPDATER{session_id}", scheduler)
        game = self.sessions.pop(session_id, [])
        [self.user_sessions.pop(user.user_id, None) for user in (game.w, game.b)]
        await wsManager.close((session_id + "w", session_id + "b"))
        return game
