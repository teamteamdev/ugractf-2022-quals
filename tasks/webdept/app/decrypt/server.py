#!/usr/bin/env python3

import base64
import os
import sys

import aiohttp.web as web
import aiohttp_jinja2 as jinja2

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from jinja2 import FileSystemLoader


BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
TMP_DIR = sys.argv[2] if len(sys.argv) >= 3 else STATE_DIR


def build_app():
    # pylint: disable=unused-variable

    app = web.Application()
    routes = web.RouteTableDef()
    routes.static('/static', 'static')

    key = os.environ['ENCRYPT_KEY'].encode()

    @routes.get('/')
    async def main_page(request):
        result = ''
        if 'enc' in request.query:
            try:
                iv, ciphertext = request.query['enc'].strip().split('|')
                iv = base64.b64decode(iv)
                ciphertext = base64.b64decode(ciphertext)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                unpad(cipher.decrypt(ciphertext), AES.block_size)
                result = 'Успех! Результат расшифровки отправлен на печать.'
            except (ValueError, KeyError):
                result = 'Данное сообщение не может быть расшифровано. Возможно, оно повреждено.'

        return jinja2.render_template('main.html', request, {'result': result})

    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))
    return app


def main():
    app = build_app()
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()
