#!/usr/bin/env python3

import aiohttp
import aiohttp.web as web
import aiohttp_jinja2 as jinja2

import hmac
import json
import os
import sys
import random
import qrcode

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
STATIC_DIR = os.path.join(BASE_DIR, "static")

PREFIX = "ugra_i_specifically_requested_the_opposite_of_this_"
SECRET2 = b"aer8Fai2Uaxu4Ooquo7sim"
SALT2_SIZE = 12


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


def qr(text):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=1, border=0)
    q.add_data(text)
    return q.make_image()


def make_app(state_dir):
    app = web.Application()
    routes = web.RouteTableDef()


    @routes.get("/{token}/")
    async def main(request):
        token = request.match_info["token"]
        q = qr(get_flag(token))
        size = q.size[0] + 9
        size -= size % 2  # just in case
        return jinja2.render_template("main.html", request, {"size": size})


    @routes.get("/{token}/ws")
    async def websocket_handler(request):
        token = request.match_info["token"]

        ws = web.WebSocketResponse(heartbeat=5, receive_timeout=10, timeout=10, max_msg_size=2048)
        await ws.prepare(request)

        q = qr(get_flag(token))
        size = q.size[0] + 9
        size -= size % 2  # just in case
        valid_points = {(x + 4, y + 4) for x in range(q.size[0]) for y in range(q.size[1]) if q.getpixel((x, y)) == 0}

        game = {"size": size, "target": [7, 7], "head": [28, 28], "tail": "DDD", "score": 0}

        await ws.send_json(game)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                for c in msg.data:
                    if c in {"U", "D", "L", "R"}:
                        oldhead = game["head"][:]
                        if c == "U":
                            game["head"][1] -= 1
                            game["tail"] = "D" + game["tail"]
                        elif c == "D":
                            game["head"][1] += 1
                            game["tail"] = "U" + game["tail"]
                        elif c == "L":
                            game["head"][0] -= 1
                            game["tail"] = "R" + game["tail"]
                        elif c == "R":
                            game["head"][0] += 1
                            game["tail"] = "L" + game["tail"]
                        else:
                            game["error"] = "Invalid data received from client"

                        if game["head"] != game["target"]:
                            game["tail"] = game["tail"][:-1]

                        snake_points = {tuple(game["head"])}
                        h = game["head"][:]
                        for c in game["tail"]:
                            if c == "U":
                                h[1] -= 1
                            elif c == "L":
                                h[0] -= 1
                            elif c == "D":
                                h[1] += 1
                            elif c == "R":
                                h[0] += 1
                            snake_points.add(tuple(h))
                        
                        if not (0 <= game["head"][0] < size) or not (0 <= game["head"][1] < size):
                            game["head"] = oldhead
                            game["error"] = "Snek has crashed into a wall"
                        if len(snake_points) < len(game["tail"]) + 1:
                            game["error"] = "Snek has crashed into itself"

                        if game["head"] == game["target"]:
                            valid_targets = valid_points - snake_points
                            if not valid_targets:
                                game["error"] = ("Unable to place new target because all permitted "
                                                 "target locations are already occupied by snek")
                                game["target"] = None
                            game["target"] = list(random.choice(list(valid_targets)))
                            game["score"] += 10
                    else:
                        game["error"] = "Invalid data received from client"

                await ws.send_json(game)
                if "error" in game:
                    return ws
            elif msg.type == aiohttp.WSMsgType.ERROR:
                return ws


    routes.static("/static", STATIC_DIR)


    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


if __name__ == "__main__":
    app = build_app()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(STATE_DIR, "snekpeek.sock"))
