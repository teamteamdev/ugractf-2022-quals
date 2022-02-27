#!/usr/bin/env python3

import os.path
import sys
import json
import hmac
import PIL.Image

PREFIX = "ugra_esc_pos_goes_lprrrrrrrr_"
SECRET1 = b"aen4Ixo8eevieghohXaifeiNg"
SALT1_SIZE = 16
SECRET2 = b"aeWa2Be1raekei4uiNgeijeiD"
SALT2_SIZE = 12

user_id = sys.argv[1]
target_dir = sys.argv[2]


def get_user_tokens(user_id):
    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


token, flag = get_user_tokens(user_id)

static_dir = os.path.join(target_dir, "static")
os.makedirs(static_dir, exist_ok=True)

img = PIL.Image.open(os.path.join("app", "full.png"))

N = int(token, 16) // 1337
left = (N // 1000000) % 100
top = (N // 10000) % 100
right = img.size[0] - (N // 100) % 100 - 32
bottom = img.size[1] - N % 100
img.crop(left, top, right, bottom).save(os.path.join(static_dir, "thermal-printme.png"))

json.dump({"flags": [flag], "urls": [f"https://thermal.{{hostname}}/{token}/"]}, sys.stdout)
