import json
import aiohttp_jinja2
import bootstrap
from aiohttp import web
from engine import SessionManager
db = bootstrap.DB().getInstance()
scheduler = bootstrap.Scheduler().getInstance()



@aiohttp_jinja2.template('index.html')
async def index(request: web.Request):
    game_id = request.url.path.split('/')[1]
    side = request.url.path.split('/')[2]
    game = SessionManager.game(game_id)
    if not game:
        return {"game_end": True}
    return {"game_id": game_id, "side": side}


async def get_opponent(request: web.Request):
    data = await request.post()
    game = SessionManager.game(data.get("game_id"))
    if not game:
        return
    user = game.get_user(data.get("side")).__dict__
    opponent = game.get_user(game.turn.opposite(data.get("side")).value)
    opponent = opponent.__dict__
    data = {"pgn": game.pgn,
            "opponent_elo": opponent.get("elo", "Нет данных"),
            "opponent_username": opponent.get("username", "Нет данных"),
            "turn": game.turn.value,
            **user}
    print(data)
    return web.Response(status=200, body=json.dumps(data),
                        content_type="application/json")


