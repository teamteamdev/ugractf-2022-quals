#!/usr/bin/env python3

import hmac
import json
import sys

PREFIX = "ugra_as_easy_as_it_gets_"
SECRET2 = b"fspodhfglkishgsldkfgjdsfhgldsfgu;koilkhj"
SECRET1 = b"flsdkfjlskdfjlsdkfj"


def get_user_tokens(user_id):
    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:16]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:12]

    return token, flag


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    token, flag = get_user_tokens(user_id)

    json.dump({"flags": [flag], "urls": [f"https://onaplate.{{hostname}}/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
