
from typing import Union
import bootstrap
from engine.user import User, Site

bot = bootstrap.MyBot().getInstance()
scheduler = bootstrap.Scheduler().getInstance()
db = bootstrap.DB().getInstance()
win_sticker = 'CAACAgIAAxkBAAEJ32ZkyCM9-t-htc-zvFWWQTgVJXkCWQACFQADwDZPE81WpjthnmTnLwQ'


class Game:
    def __init__(self, session_id, SessionManager):
        from websocket import wsManager
        self.wsManager = wsManager
        self.SessionManager = SessionManager
        self.session_id: str = session_id
        self.pgn: Union[str,None] = None
        self.w: Union[User, None] = None
        self.b: Union[User, None] = None
        self.turn: Site = Site.WHITE
        self.time: int = 30
        self.current_connect_time: int = 0
        self.check: bool = False
        self.checked: dict = {Site.WHITE: False, Site.BLACK: False}

    def get_user(self, site=None):
        return getattr(self, site or self.turn.convert())

    def update_user(self, side: Site, data: dict):
        user = self.get_user(side.convert())
        for key, value in data.items():
            setattr(user, key, value)

    async def timer(self):
        if self.current_connect_time >= 60:
            await self.time_out()
            return
        if self.get_user().passed >= 2:
            text_loser = "Вы 2 раза подряд пропустили ход, поэтому вам присуждается поражение"
            text_winner = "Ваш соперник 2 раза подряд пропустил ход, поэтому вам присуждается победа"

            await self.game_over(winner=self.turn.opposite(),
                                 text_winner=text_winner, text_loser=text_loser)
            return
        if self.time <= 0:
            opponent = self.turn.opposite()
            self.get_user().passed += 1
            if self.check:
                text_loser = "Вы не ушли из-под шаха, поэтому вам присуждается поражение"
                text_winner = "Ваш соперник не ушел из-под шаха, поэтому вам присуждается победа"
                await self.game_over(winner=self.turn.opposite(),
                                     text_winner=text_winner, text_loser=text_loser)

            self.turn = opponent
            self.time = 30
            self.check = False

        if all(self.checked.values()):
            self.current_connect_time = 0
            self.time -= 1
            data = {
                "kind": "UPDATE",
                "payload": {
                    "turn": self.turn.convert(),
                    "remainingTime": self.time,
                    "pgn": self.pgn
                }
            }
        else:
            self.current_connect_time += 1
            data = {"kind": "CHECK"}
        await self.wsManager.send(self, data)



    async def time_out(self):
        for i in (self.b.user_id, self.w.user_id):
            await bot.send_message(chat_id=i, text="Время ожидания истекло, один или несколько игроков не подключились")
        await self.SessionManager.close(self.wsManager, self.session_id)
    async def draw(self):
        for i in (self.b.user_id, self.w.user_id):
            await bot.send_message(chat_id=i, text="Игра окончена, была взята ничья!")
        await self.SessionManager.close(self.wsManager, self.session_id)

    async def disconnected(self, discconected_id):
        for i in (self.b.user_id, self.w.user_id):
            text = ("Вы вышли из игры", "Ваш соперник вышел из игры")[str(i) != str(discconected_id)]
            await bot.send_message(chat_id=i, text=text)
        await self.SessionManager.close(self.wsManager, self.session_id)

    async def game_over(self, winner: Site, text_winner:str, text_loser:str):
        data = {"kind": "GAMEOVER",
                "payload": {
                    "winner": winner.convert(),
                    "text_loser": text_loser,
                    "text_winner": text_winner,
                    }
                }
        await self.wsManager.send(self, data)
        await self.SessionManager.close(self.wsManager, self.session_id)
        if self.pgn:
            await db.add_game_history(str(self.w.user_id), str(self.b.user_id), self.pgn)
        loser = self.turn.opposite(side=winner.convert())
        winner_user = getattr(self, winner.convert())
        loser_user = getattr(self, loser.convert())
        await db.update_users_stats(str(winner_user.user_id), str(loser_user.user_id))
        await bot.send_message(winner_user.user_id, "Поздравляю, вы выиграли!")
        await bot.send_sticker(chat_id=winner_user.user_id, sticker=win_sticker)
        await bot.send_message(loser_user.user_id, "Проигрывать тоже полезно...")

