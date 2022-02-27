#!/usr/bin/env python3

import aiohttp
import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import base64

import hmac
import io
import json
import os
import sys
import struct

import lzo
import PIL.Image

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
STATIC_DIR = os.path.join(BASE_DIR, "static")

PREFIX = "ugra_esc_pos_goes_lprrrrrrrr_"
SECRET2 = b"aeWa2Be1raekei4uiNgeijeiD"
SALT2_SIZE = 12

IMAGE = PIL.Image.open(os.path.join(BASE_DIR, "full.png"))


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


def image_as_bytes(img):
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()


def make_app(state_dir):
    app = web.Application()
    routes = web.RouteTableDef()


    @routes.get("/{token}/")
    async def main(request):
        return jinja2.render_template("main.html", request, {})


    @routes.post("/{token}/")
    async def do_print(request):
        token = request.match_info["token"]

        data_reader = await request.multipart()

        field = await data_reader.next()
        while field and field.name != "data":
            field = await data_reader.next()

        if not field:
            return jinja2.render_template("main.html", request, {"error": True})
        try:
            printer_data = bytes(await field.read())
        except:
            return jinja2.render_template("main.html", request, {"error": True})

        if len(printer_data) > 2 ** 18:
            return jinja2.render_template("main.html", request, {"error_big": True})

        result_images = []
        while b"\x1Dv00" in printer_data:
            printer_data = printer_data[printer_data.find(b"\x1Dv00")+4:]
            if len(printer_data) < 8:
                break

            width, height = struct.unpack("<HH", printer_data[0:4])
            data_len, = struct.unpack("<L", printer_data[4:8])
            lzo_data = printer_data[8:8 + data_len]
            printer_data = printer_data[8 + data_len:]

            if width == 0 or height == 0 or width > 1248 // 8 or height > 16:
                continue

            try:
                image_bits = lzo.decompress(lzo_data, False, width * height)
            except:
                continue

            result = PIL.Image.new("1", (width * 8, height), 1)
            result.putdata(sum([[1 - (c >> b) & 1 for b in [7, 6, 5, 4, 3, 2, 1, 0]] for c in image_bits], []))

            result_images.append(result)
            if len(result_images) > 128:
                return jinja2.render_template("main.html", request, {"error_high": True})

        flag = None
        if not result_images:
            result = PIL.Image.new("1", (1248, 1), 1)
        else:
            result = PIL.Image.new("1", (1248, sum(r.size[1] for r in result_images)), 1)
            cy = 0
            for r in result_images:
                result.paste(r, (0, cy))
                cy += r.size[1]

            try:
                N = int(token, 16) // 1337
            except:
                N = 12345678
            left = ((N // 1000000) % 100) & 0xfff8
            top = (N // 10000) % 100
            right = (IMAGE.size[0] - (N // 100) % 100 - 32) & 0xfff8
            bottom = IMAGE.size[1] - N % 100

            if bottom - top == result.size[1]:
                bytes_result = image_as_bytes(result)
                crop = IMAGE.crop((left, top, right, bottom))

                test = result.copy()
                test.paste(crop, (0, 0))
                bytes_test = image_as_bytes(test) 
                if bytes_result == bytes_test:
                    flag = get_flag(token)

        return jinja2.render_template("main.html", request,
                                      {"result": base64.b64encode(image_as_bytes(result)).decode(),
                                       "flag": flag})


    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


if __name__ == "__main__":
    app = build_app()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(STATE_DIR, "thermal.sock"))
