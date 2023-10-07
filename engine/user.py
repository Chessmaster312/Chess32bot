from enum import Enum
from typing import Union


class User:
    '''Класс хранящий данные об игроке.\n
    `remaining_attempts` - количество возможных прибавлений времени,\n
    `premium` - наличие подписки,\n
    `user_id` - ID пользователя,\n
    `draw` - предлагал ничью?,\n
    `username` - имя пользователя,\n
    `elo` - ранг игрока '''

    def __init__(self, premium: bool, user_id: str, username: str, elo: int):
        self.remaining_attempts: int = 3
        self.elo: int = elo
        self.passed: int = 0
        self.premium: bool = premium
        self.draw: bool = False
        self.user_id: str = user_id
        self.username: str = username


class Site(Enum):
    WHITE = 'w'
    BLACK = 'b'

    def opposite(self, side=None):
        return [Site.WHITE, Site.BLACK][(side or self) == Site.WHITE]

    def convert(self=None, side=None):
        if side is None and self:
            return self.value
        return Site(side)
