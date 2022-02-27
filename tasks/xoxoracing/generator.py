#!/usr/bin/env python3

import os.path
import sys
import json
import hmac

PREFIX = "ugra_go_go_go_come_on_yes_yes_a_bit_more_just_a_little_"
SECRET1 = b"seekuk9afahy8aiRee6dieyeechoo3eec0rai"
SALT1_SIZE = 16
SECRET2 = b"HaiTahsief4uphieShiengahph3ooLooQu6ai"
SALT2_SIZE = 15

user_id = sys.argv[1]
target_dir = sys.argv[2]


def get_user_tokens(user_id):
    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


token, flag = get_user_tokens(user_id)

json.dump({"flags": [flag], "urls": [f"https://xoxoracing.{{hostname}}/{token}/"]}, sys.stdout)
