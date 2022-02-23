#!/usr/bin/env python3

import hmac
import json
import sys

PREFIX = "ugra_i_wish_fermat_had_css_"
SECRET1 = b"iem9Eixo2ahdengaisak3sheich6aucev"
SALT1_SIZE = 16
SECRET2 = b"to0Gohl2thahheeghae6te"
SALT2_SIZE = 12


def get_user_tokens(user_id):
    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    token, flag = get_user_tokens(user_id)

    json.dump({"flags": [flag], "urls": [f"https://margin.{{hostname}}/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
