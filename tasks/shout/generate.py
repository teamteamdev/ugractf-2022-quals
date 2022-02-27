#!/usr/bin/env python3

import hmac
import json
import os
import random
import sys

PREFIX = "ugra_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa_"
TOKEN_SECRET = b"executive-contribution-marketing-consideration-brilliance"
TOKEN_SIZE = 12
TOKEN_SIGNATURE = b"nightmare-premature-reasonable-dangerous-negotiation"
SIGNATURE_SIZE = 12
FLAG_SECRET = b"hypothesize-underline-representative-coincidence-appearance"
SALT_SIZE = 16


def get_user_tokens(user_id):
    token = hmac.new(TOKEN_SECRET, str(user_id).encode(), "sha256").hexdigest()[:TOKEN_SIZE]
    token += hmac.new(TOKEN_SIGNATURE, str(token).encode(), "sha256").hexdigest()[:SIGNATURE_SIZE]
    flag = PREFIX + hmac.new(FLAG_SECRET, str(token).encode(), "sha256").hexdigest()[:SALT_SIZE]
    return token, flag


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    token, flag = get_user_tokens(user_id)

    json.dump({"flags": [flag], "bullets": [f"Токен: <code>{token}</code>"]}, sys.stdout)


if __name__ == "__main__":
    generate()
