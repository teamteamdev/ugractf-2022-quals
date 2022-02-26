#!/usr/bin/env python3

import aiohttp.web as web
import aiohttp_jinja2 as jinja2

import base64
import os

from jinja2 import FileSystemLoader

from encrypt import encrypt as encrypt_bytes

BASE_DIR = os.path.dirname(__file__)


def make_app():
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/")
    async def main(request):
        return jinja2.render_template("main.html", request, {"encrypted": None})


    @routes.post("/")
    async def encrypt(request):
        form = await request.post()
        content = form.get("data", "").encode()

        if len(content) > 32:
            raise web.HTTPBadRequest(text="Слишком длинный текст")

        return jinja2.render_template("main.html", request, {"encrypted": base64.b64encode(encrypt_bytes(content)).decode()})


    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


if __name__ == "__main__":
    app = make_app()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(STATE_DIR, "betagost.sock"))
