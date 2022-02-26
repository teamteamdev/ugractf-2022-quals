#!/usr/bin/env python3

import hmac
import json
import os
import random
import sys

PREFIX = "ugra_lfsr_is_so_cyclic_"
FLAG_SECRET = b"dependence-housewife-mastermind-overwhelm-girlfriend"
SALT_SIZE = 16

SECRET = 174807

class Stream:
    value = 1

    @classmethod
    def bit(cls) -> int:
        b = 0
        i = 0

        while SECRET > 2 ** i:
            b ^= (SECRET >> i) & (cls.value >> i) & 1
            i += 1
        
        cls.value = ((b << i) | cls.value) >> 1

        return b

    @classmethod
    def byte(cls) -> int:
        for _ in range(8):
            cls.bit()
        return cls.value & 255


def encrypt(plaintext: bytes) -> bytes:
    return bytes(
        byte ^ Stream.byte()
        for byte in plaintext
    )


def get_flag(user_id):
    return PREFIX + hmac.new(FLAG_SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    rnd = random.Random(f"{user_id}-gogogornd")
    target_dir = sys.argv[2]
    flag = get_flag(user_id)

    offset = rnd.randint(10000, 121000)
    for _ in range(offset):
        Stream.bit()

    os.makedirs(os.path.join(target_dir, "attachments"), exist_ok=True)
    with open(os.path.join(target_dir, "attachments", "flag.enc"), "wb") as flag_file:
        flag_file.write(encrypt(flag.encode()))

    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
