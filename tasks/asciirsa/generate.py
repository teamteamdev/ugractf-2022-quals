#!/usr/bin/env python3

import hmac
import json
import os
import random
import sys

PREFIX = "ugra_dont_roll_asciirsa_crypto_"
FLAG_SECRET = b"chauvinist-photocopy-conservative-executrix-difference"
SALT_SIZE = 16


def get_flag(user_id):
    return PREFIX + hmac.new(FLAG_SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    target_dir = sys.argv[2]
    flag = get_flag(user_id)

    modulo = 256
    public_key = 17

    flag_encrypted = []
    for c in flag:
        char_code = ord(c) * 2 - 1
        encrypted_char_code = pow(char_code, public_key, modulo)
        flag_encrypted.append(encrypted_char_code)

    os.makedirs(os.path.join(target_dir, "attachments"), exist_ok=True)
    with open(os.path.join(target_dir, "attachments", "rsa.enc"), "wb") as flag_file:
        flag_file.write(bytes(flag_encrypted))

    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
