#!/usr/bin/env python3

import aiohttp
import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import asyncio

import hmac
import io
import json
import os
import sys
import random
import time

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
STATIC_DIR = os.path.join(BASE_DIR, "static")

PREFIX = "ugra_go_go_go_come_on_yes_yes_a_bit_more_just_a_little_"
SECRET2 = b"HaiTahsief4uphieShiengahph3ooLooQu6ai"
SALT2_SIZE = 15


ROUND_TIME = 32

TEXT = open(os.path.join(BASE_DIR, "text.txt")).read().strip()
def gen_text():
    return TEXT[random.randint(0, len(TEXT) - 41):][:40]


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


def make_app(state_dir):
    app = web.Application()
    routes = web.RouteTableDef()


    @routes.get("/{token}/")
    async def main(request):
        return jinja2.render_template("main.html", request, {})


    @routes.get("/{token}/ws")
    async def play(request):
        token = request.match_info["token"]

        flag = get_flag(token)

        ws = web.WebSocketResponse(heartbeat=5, receive_timeout=15, timeout=15, max_msg_size=2048)
        await ws.prepare(request)

        game = {"score": 0, "text": gen_text(), "key": None, "deadline": time.time() + ROUND_TIME}

        await ws.send_json({"countdown": ROUND_TIME, "flag": ""})

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = msg.json()
                except:
                    await ws.send_json({"error": "malformed-input"})
                    return ws

                if "key" in data:
                    game["key"] = (data["key"] + "".join(chr(random.randint(0, 255)) for _ in range(40)))[:40]
                    clamp = lambda x: x if 32 <= x < 127 else ord("Ж")
                    await ws.send_json({"ciphertext": "".join(chr(clamp(ord(t) ^ ord(k)))
                                                              for t, k in zip(game["text"], game["key"]))})
                elif "text" in data:
                    status = "red"
                    if data["text"] == game["text"]:
                        status = "yellow"
                        if time.time() < game["deadline"]: 
                            status = "green"
                            game["score"] += random.randint(2, 6)
                    await ws.send_json({"status": status, "text": game["text"], "flag": flag[:game["score"]]})

                    await asyncio.sleep(2 + random.random() * 2)
                    game["text"] = gen_text()
                    game["key"] = None
                    game["deadline"] = time.time() + ROUND_TIME
                    await ws.send_json({"status": "", "countdown": ROUND_TIME})
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
        web.run_app(app, path=os.path.join(STATE_DIR, "xoxoracing.sock"))
