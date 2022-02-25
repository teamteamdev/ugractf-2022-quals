#!/usr/bin/env python3

import base64
import functools
import hmac
import os
import secrets
import sys

import aiohttp
import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import aiohttp_session as sessions
import aiohttp_session.cookie_storage as storage
import aiosqlite

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from jinja2 import FileSystemLoader


BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
TMP_DIR = sys.argv[2] if len(sys.argv) >= 3 else STATE_DIR

PREFIX = [
    "ugra_isolate_your_public_hosts_",
    "ugra_do_not_ever_use_cbc_"
]

TOKEN_SECRET = b"blackmail-mechanism-willpower-enthusiasm-determine"
TOKEN_SALT_SIZE = 16

FLAG_SECRET = [
    b"conservation-systematic-revolutionary-professor-correspond",
    b"nationalism-champagne-translate-tournament-projection"
]
FLAG_SALT_SIZE = 12


def verify_token(token):
    left_token, right_token = token[:TOKEN_SALT_SIZE], token[TOKEN_SALT_SIZE:]

    signature = hmac.new(TOKEN_SECRET, left_token.encode(), 'sha256').hexdigest()[:TOKEN_SALT_SIZE]

    return signature == right_token


def get_flag(token, i):
    return PREFIX[i] + hmac.new(FLAG_SECRET[i], token.encode(), "sha256").hexdigest()[:FLAG_SALT_SIZE]


def get_db_path(token):
    return os.path.join(STATE_DIR, f'{token}.db')


key = os.environ['ENCRYPT_KEY'].encode()

def encrypt(message):
    cipher = AES.new(key, AES.MODE_CBC)
    padded = pad(message.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    iv = base64.b64encode(cipher.iv).decode()
    ciphertext = base64.b64encode(encrypted).decode()

    return f'{iv}|{ciphertext}'


async def init_database(token):
    path = get_db_path(token)
    if os.path.exists(path):
        return

    async with aiosqlite.connect(path) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS request (
            id INTEGER PRIMARY KEY,
            author TEXT NOT NULL,
            data TEXT NOT NULL
        )''')
        await db.execute(f'''INSERT INTO request (author, data) VALUES (
            'ivanovas', '{encrypt(get_flag(token, 1))}'
        )''')
        await db.commit()


def build_app():
    # pylint: disable=unused-variable

    app = web.Application()
    routes = web.RouteTableDef()
    routes.static('/static', 'static')

    def with_auth(func):
        @functools.wraps(func)
        async def wrapper(request):
            token = request.match_info['token']
            if not verify_token(token):
                raise web.HTTPBadRequest()

            session = await sessions.get_session(request)
            if 'user' not in session:
                return web.HTTPSeeOther(f'/{token}/auth')

            await init_database(token)

            return await func(request, session['user'], token)
        return wrapper


    def add_backend(func):
        @functools.wraps(func)
        async def wrapper(request):
            response = await func(request)
            response.headers['X-Backend'] = '10.13.37.159'
            return response
        return wrapper


    @routes.get('/{token}/')
    @add_backend
    async def main_page(request):
        session = await sessions.get_session(request)
        token = request.match_info['token']

        if 'user' in session:
            raise web.HTTPSeeOther(f'/{token}/dashboard')
        else:
            raise web.HTTPSeeOther(f'/{token}/auth')

    @routes.get('/{token}/auth')
    @add_backend
    async def auth_page(request):
        return jinja2.render_template('login.html', request, {})

    @routes.post('/{token}/auth')
    @add_backend
    async def auth_action(request):
        token = request.match_info['token']

        timeout = aiohttp.ClientTimeout(total=0.5)
        try:
            body = await request.post()
            username = body['username']
            code = body['code']
            async with aiohttp.ClientSession(timeout=timeout) as rsession:
                async with rsession.post('http://10.13.37.62/check-otp', data={
                        'username': username,
                        'code': code
                }) as resp:
                    response = await resp.json()
                    if response.get('error') == 'invalid':
                        return web.Response(body="Неверный код", status=403)
                    if response.get('error') == 'bad-request':
                        raise web.HTTPBadRequest()
                    if response.get('status') != 'ok':
                        raise web.HTTPInternalServerError()
        except KeyError:
            raise web.HTTPBadRequest()
        except:
            raise web.HTTPGatewayTimeout()

        session = await sessions.get_session(request)
        session['user'] = username
        session.changed()

        return web.HTTPSeeOther(f'/{token}/dashboard')


    @routes.get('/{token}/dashboard')
    @add_backend
    @with_auth
    async def dashboard_page(request, user, token):
        return jinja2.render_template('dashboard.html', request, {
            'user': user,
            'flag': get_flag(token, 0),
            'token': token
        })

    @routes.post('/{token}/dashboard')
    @add_backend
    @with_auth
    async def dashboard_action(request, user, token):
        timeout = aiohttp.ClientTimeout(total=0.5)
        try:
            body = await request.post()
            async with aiohttp.ClientSession(timeout=timeout) as rsession:
                async with rsession.get(body['url']) as resp:
                    text = await resp.read()
                    try:
                        text = text.decode('utf-8')
                    except UnicodeDecodeError:
                        text = str(text)[2:-1]
        except KeyError:
            raise web.HTTPBadRequest()
        except:
            raise web.HTTPBadGateway()

        return jinja2.render_template('result.html', request, {
            'url': body['url'],
            'response': text,
            'user': user,
            'token': token
        })


    @routes.get('/{token}/dashboard/helpdesk')
    @add_backend
    @with_auth
    async def helpdesk_page(request, user, token):
        if user == 'admin':
            async with aiosqlite.connect(get_db_path(request.match_info['token'])) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM request ORDER BY id DESC') as cur:
                    requests = await cur.fetchall()
        else:
            requests = []

        return jinja2.render_template('hd.html', request, {
            'user': user,
            'requests': requests,
            'token': token,
            'ok': request.query.get('ok') is not None
        })

    @routes.post('/{token}/dashboard/helpdesk')
    @add_backend
    @with_auth
    async def helpdesk_action(request, user, token):
        try:
            body = await request.post()
            message = body['text']
        except KeyError:
            raise web.HTTPBadRequest()

        encrypted = encrypt(message)

        async with aiosqlite.connect(get_db_path(token)) as db:
            await db.execute(f'''INSERT INTO request (author, data) VALUES (
                '{user}', '{encrypted}'
            )''')
            await db.execute(f'''DELETE FROM request WHERE id IN (SELECT id FROM request WHERE author = '{user}' ORDER BY id DESC LIMIT 1000 OFFSET 5)''');
            await db.commit()

        raise web.HTTPSeeOther(f'/{token}/dashboard/helpdesk?ok')

    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))
    sessions.setup(app, storage.EncryptedCookieStorage(secrets.token_bytes(32)))
    return app


def main():
    app = build_app()
    web.run_app(app, path=os.path.join(TMP_DIR, 'webdept.sock'))


if __name__ == '__main__':
    main()
