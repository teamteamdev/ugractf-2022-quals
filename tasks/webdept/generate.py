#!/usr/bin/env python3

import hmac
import json
import sys

TASKS = [
    "webdept1",
    "webdept2"
]

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


def get_token():
    user_id = sys.argv[1]

    token1 = hmac.new(TOKEN_SECRET, str(user_id).encode(), "sha256").hexdigest()[:TOKEN_SALT_SIZE]
    token2 = hmac.new(TOKEN_SECRET, token1.encode(), "sha256").hexdigest()[:TOKEN_SALT_SIZE]

    return token1 + token2


def get_flag(i, token):
    return PREFIX[i] + hmac.new(FLAG_SECRET[i], token.encode(), "sha256").hexdigest()[:FLAG_SALT_SIZE]


def generate():
    if len(sys.argv) != 4:
        print("Usage: generate.py user_id target_dir tasks", file=sys.stderr)
        sys.exit(1)

    token = get_token()

    json.dump({
        TASKS[i]: {
            "flags": [get_flag(i, token)],
            "substitutions": {},
            "urls": [
                f"https://webdept.{{hostname}}/{token}/"
            ]
        }
        for i in range(len(TASKS))
    }, sys.stdout)


if __name__ == "__main__":
    generate()
