#!/usr/bin/env python3

import aiohttp.web as web
import aiohttp_jinja2 as jinja2

import hmac
import os
import sys

import validator

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "ugra_i_wish_fermat_had_css_"
SECRET2 = b"to0Gohl2thahheeghae6te"
SALT2_SIZE = 12

VALIDATOR_SOURCE = open(os.path.join(BASE_DIR, "validator.py"), "rb").read()


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()


    @routes.get("/{token}/validator.py")
    async def source(request):
        resp = web.StreamResponse()
        resp.headers["Content-type"] = "text/plain"
        await resp.prepare(request)
        await resp.write(VALIDATOR_SOURCE)
        return resp


    @routes.get("/{token}/")
    async def main(request):
        return jinja2.render_template("main.html", request, {"errors": {}, "flag": None, "form": {}})


    @routes.post("/{token}/")
    async def check(request):
        token = request.match_info["token"]
        form = await request.post()
        flag = None

        errors = validator.validate(form)
        if errors == {}:
            flag = get_flag(token)

        return jinja2.render_template("main.html", request, {"errors": errors, "flag": flag, "form": form})


    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


if __name__ == "__main__":
    app = build_app()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(STATE_DIR, "margin.sock"))
