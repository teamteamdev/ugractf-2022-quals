#!/usr/bin/env python3

import aiohttp.web as web

import urllib.parse as up
import hmac
import os
import sys

import validator

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "ugra_as_easy_as_it_gets_"
SECRET2 = b"fspodhfglkishgsldkfgjdsfhgldsfgu;koilkhj"
SALT2_SIZE = 12

PLATE = open(os.path.join(BASE_DIR, "plate.jpg"), "rb").read()
PAGE  = open(os.path.join(BASE_DIR, "page.html"), "rb").read()


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


def make_app():
    app = web.Application()
    routes = web.RouteTableDef()


    @routes.get("/{token}/")
    async def source(request):
        resp = web.StreamResponse()
        resp.headers["Content-type"] = "text/html"
        await resp.prepare(request)
        await resp.write(PAGE)
        return resp


    @routes.get("/{token}/plate.jpg")
    async def source(request):
        resp = web.StreamResponse()
        resp.headers["Content-type"] = "image/jpg"
        await resp.prepare(request)
        await resp.write(PLATE)
        return resp


    @routes.get("/{token}/fl4g%3Fis%3Fh%23r3")
    async def source(request):
        token = request.match_info["token"]
        resp = web.StreamResponse()
        resp.headers["Content-type"] = "text/plain"
        await resp.prepare(request)
        await resp.write(get_flag(token).encode())
        return resp


    app.add_routes(routes)
    return app


if __name__ == "__main__":
    app = make_app()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(STATE_DIR, "onaplate.sock"))
