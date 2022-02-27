#!/usr/bin/env python3
# -*- coding: utf-8 _*_

import asyncio
import aiohttp
import os
import sys
from random import choice
import hmac

PREFIX = "ugra_every_big_thing_consists_of_many_little_ones_"
SECRET1 = b"reuse-reduce-ecyce"
SALT1_SIZE = 32
SECRET2 = b"god-give-me-strength-i-wanna-sleep"
SALT2_SIZE = 12

BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "art.asc"), "r") as f:
    ART = f.read()

GREET_M = "КОРПОРАТИВНАЯ СИСТЕМА\t\t\t2022 ГОД\n\nКОРПОРАТИВНЫЙ НОМЕР ТЕЛЕФОНА В ФОРМАТЕ 7ХХХХХХХХХХ: "
SECRET_M = "\n\nОБЩИЙ СЕКРЕТ НА 02.2022: "
SECRET_P = "severomorsk"
CLEAR_M = "\u001B[2J"


def generate_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


async def calculate_ip(ip):
    url = f"https://api.freegeoip.app/json/{ip}?apikey=03d03d10-97fe-11ec-b934-4b5324d47765"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp = await resp.json()
            country = resp.get("country_name", "[Неизвестная]") or "[Скрытное]"
            city = resp.get("city", "[Неизвестный]") or "[Скрытное]"
            return ', '.join((country, city))


async def game(reader, writer):
    async def send(msg):
        writer.write(msg.encode('utf8'))
        await writer.drain()

    async def recv():
        data = await reader.readline()
        if data:
            return data.decode().strip().lower()
        else:
            return ""

    await send(GREET_M)
    token = await recv()
    while len(token) < 11:
        await send("НЕВЕРНО\nКОРПОРАТИВНЫЙ НОМЕР ТЕЛЕФОНА В ФОРМАТЕ 7ХХХХХХХХХХ: ")
        token = await recv()

    await send(SECRET_M)
    password = await recv()
    tries = 0
    while password != SECRET_P:
        await send("НЕВЕРНО\nОБЩИЙ СЕКРЕТ НА 02.2022: ")
        tries += 1
        if tries > 2:
            await send("\n")
            writer.close()
        token = await recv()

    ip = reader._transport.get_extra_info('peername')[0]
    await send(CLEAR_M)
    await send(ART)
    await asyncio.sleep(1)
    geoip = await calculate_ip(ip)
    await send("\n\nЗагрузка Корпоративной Среды завершена.\n\nВ Н И М А Н И Е !\n\nОБНАРУЖЕНА ПОПЫТКА НЕСАНКЦИОНИРОВАННОГО ДОСТУПА К КОРПОРАТИВНОЙ ИНФРАСТРУКТУРЕ.\nНАРУШИТЕЛЬ ЗАФИКСИРОВАН. ИНЦИДЕНТ ЗАФИКСИРОВАН.\n\n")
    await send(f"IP-АДРЕС МЕСТА НАРУШЕНИЯ: {ip}\n")
    await send(f"ЛОКАЦИЯ НАРУШИТЕЛЯ: {geoip}\n")
    await send(f"ВНУТРЕННИЙ ИДЕНТИФИКАТОР НСД: {'+7' + generate_flag(token)}\n")

    writer.close()


def start():
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(game, '0.0.0.0', 64738)
    print('Starting server...')
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    start()
