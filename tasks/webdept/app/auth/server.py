#!/usr/bin/env python3

import base64
import hashlib
import hmac
import io
import os
import struct
import sys
import time

import aiohttp.web as web
import qrcode


BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
TMP_DIR = sys.argv[2] if len(sys.argv) >= 3 else STATE_DIR


def build_app():
    # pylint: disable=unused-variable

    app = web.Application()
    routes = web.RouteTableDef()

    def get_hotp_token(secret, intervals_no):
        key = base64.b32decode(secret, True)
        message = struct.pack(">Q", intervals_no)
        digest = hmac.new(key, message, hashlib.sha1).digest()
        offset = digest[19] & 15
        return (struct.unpack(">I", digest[offset:offset+4])[0] & 0x7fffffff) % 1000000


    def get_totp_token(secret):
        return get_hotp_token(secret, intervals_no=int(time.time())//30)


    def get_otp_secret(username):
        return base64.b32encode({
            'admin': '017554320',
            'andy77': '626239889'
        }[username].encode()).decode()


    @routes.get('/')
    async def main_page(request):
        return web.json_response({
            "api": {
                "schema": {
                    "request-otp": {
                        "method": "GET",
                        "path": "/request-otp",
                        "parameters": {
                            "username": {
                                "type": "string",
                                "in": "querystring",
                                "required": "true"
                            }
                        }
                    },
                    "check-otp": {
                        "method": "POST",
                        "path": "/check-otp",
                        "parameters": {
                            "username": {
                                "type": "string",
                                "in": "body",
                                "required": "true"
                            },
                            "code": {
                                "type": "string",
                                "in": "body",
                                "required": "true"
                            }
                        }
                    }
                }
            }
        })

    @routes.get('/request-otp')
    async def request_otp(request):
        try:
            username = request.query['username']
            secret = get_otp_secret(username)
        except KeyError:
            return web.json_response(
                {"error": "bad-request"},
                status=400
            )

        qr = qrcode.make(f'otpauth://totp/webdept:{username}?secret={secret}&issuer=web')
        data = io.BytesIO()
        qr.save(data, format='png')

        return web.Response(
            body=data.getvalue(),
            headers={"Content-Type": "image/png"}
        )


    @routes.post('/check-otp')
    async def check_otp(request):
        try:
            form = await request.post()
            username = form['username']
            code = int(form['code'])
        except (KeyError, ValueError):
            return web.json_response(
                {"error": "bad-request"},
                status=400
            )

        if code != get_totp_token(get_otp_secret(username)):
            return web.json_response(
                {"error": "invalid"},
                status=403
            )

        return web.json_response(
            {"status": "ok"}
        )


    app.add_routes(routes)
    return app


def main():
    app = build_app()
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()
