#!/usr/bin/env python3

import hmac
import json
import sys

PREFIX = "ugra_i_specifically_requested_the_opposite_of_this_"
SECRET1 = b"ciepeiheu5taedeiT8ahGh"
SALT1_SIZE = 16
SECRET2 = b"aer8Fai2Uaxu4Ooquo7sim"
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

    json.dump({"flags": [flag], "urls": [f"https://snekpeek.{{hostname}}/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
