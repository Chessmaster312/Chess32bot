import json
import logging
from enum import Enum

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.client import WebSocketClientProtocol as WsClient

import bootstrap
from engine import SessionManager
from engine.user import Site

db = bootstrap.DB().getInstance()
scheduler = bootstrap.Scheduler().getInstance()


class WebSocketServer:
    host = "localhost"
    port = 80
    logger = logging.getLogger(__name__)
    connected_users: dict[str, WsClient] = {}

    async def start_server(self):
        await websockets.serve(self.new_client_connection, self.host, self.port)

    async def send(self, game, data):
        for site in (Site.WHITE, Site.BLACK):
            key = game.session_id + site.convert()
            client = self.connected_users.get(key)
            if client:
                try:
                    await client.send(json.dumps(data))
                    game.checked.update({site: True})
                except:
                    game.checked.update({site: False})
                    await self.close((key))
                    continue

    async def update(self, message, game_id, side):
        site = Site.opposite(side)
        client = self.connected_users.get(game_id + site.opposite().convert())
        try:
            await client.send(message)
        except Exception as e:
            print(str(e))
            pass

    async def new_client_connection(self, client_socket: WsClient, path: str):
        game_id = path.split('/')[1]
        side = path.split('/')[2]
        self.connected_users.update({game_id + side: client_socket})
        game = SessionManager.game(game_id)
        try:
            while self.connected_users.get(game_id + side):
                new_message = json.loads(await client_socket.recv())
                payload = new_message.get('payload', [])
                kind = new_message.get("kind")
                if hasattr(ServerEventKind, str(kind)):
                    await getattr(ServerEventKind, kind)(game, game_id, side, payload)
        except (ConnectionClosedError, ConnectionClosedOK):
            if side:
                game.checked.update({Site.convert(side=side): False})

    async def on_draw(self, game, game_id, side, __):
        await self.update(json.dumps({"kind": "DRAW"}), game_id, side)
        game.get_user(side).draw = True
    async def on_draw_accept(self, game, game_id, side, __):
        data = {"kind": "GAMEOVER",
                "payload": {
                    "winner": 'w',
                    "text_loser": "Игра окончена, была взята ничья!",
                    "text_winner": "Игра окончена, была взята ничья!",
                    }
                }
        await self.send(game, data)
        await game.draw()
    async def on_addtime(self, game, __, side, payload):
        game.time += payload.get('time')
        game.get_user(side).remaining_attempts = payload.get("remaining_attempts")


    async def on_gameover(self, game, _,__, payload):
        text_loser = payload.get('text_loser')
        text_winner = payload.get('text_winner')
        winner = payload.get('winner')
        winner = Site.convert(side=winner)
        await game.game_over(winner=winner,
                             text_loser=text_loser,
                             text_winner=text_winner)


    async def on_move(self,game, _, side, payload):
        game.pgn = payload.get("pgn")
        game.get_user(side).passed = 0
        game.turn = game.turn.opposite()
        game.time = 30
        game.check = payload.get("check")

    async def close(self, connections: tuple):
        for connection in connections:
            connection = self.connected_users.pop(connection, None)
            if connection:
                await connection.close()


class ServerEventKind(Enum):
    '''Типы событий: \n
    `MOVE` - пользователь сделал ход,\n
    `DRAW` - пользователь предложил ничью,\n
    `GAMEOVER` - игра окончена,\n
    `ADDTIME` - пользователь добавил время,\n
    '''
    MOVE = WebSocketServer().on_move
    DRAW = WebSocketServer().on_draw
    GAMEOVER = WebSocketServer().on_gameover
    ADDTIME = WebSocketServer().on_addtime
    DRAW_ACCEPT = WebSocketServer().on_draw_accept
