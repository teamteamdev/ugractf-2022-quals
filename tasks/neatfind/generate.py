#!/usr/bin/env python3

import codecs
import hmac
import json
import math
import os
import random
import sys
import tempfile

PREFIX = "ugra_every_big_thing_consists_of_many_little_ones_"
SECRET1 = b"reuse-reduce-ecyce"
SALT1_SIZE = 32
SECRET2 = b"god-give-me-strength-i-wanna-sleep"
SALT2_SIZE = 12

UNUSED_AREA_CODES = [907, 942, 943, 944, 945, 946, 947, 948, 949, 972, 973, 974, 975, 976, 990, 998]


def get_user_tokens():
    user_id = sys.argv[1]
    random.seed(user_id)
    token = f"7{random.choice(UNUSED_AREA_CODES)}{random.randint(1000000, 9888888)}"
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


def generate():
    if len(sys.argv) < 2:
        print("Usage: generate.py user_id", file=sys.stderr)
        sys.exit(1)

    token, flag = get_user_tokens()

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": [],
        "bullets": [
            f"Надпись на брелке: <code>+{token}</code>"
        ]
    }, sys.stdout)


if __name__ == "__main__":
    generate()
