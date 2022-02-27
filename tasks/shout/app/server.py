#!/usr/bin/env python3

import hmac
import os
import pathlib
import sys

PREFIX = "ugra_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA_"
FLAG_SECRET = b"hypothesize-underline-representative-coincidence-appearance"
SALT_SIZE = 16

BINARY = pathlib.Path(__file__).parent.parent / "attachments" / "shout"
TEMP_DIR = sys.argv[1]


def get_flag(token):
    return PREFIX + hmac.new(FLAG_SECRET, str(token).encode(), "sha256").hexdigest()[:SALT_SIZE]


print("Your token:", end=" ", flush=True)
token = input().strip()

os.makedirs(os.path.join(TEMP_DIR, token), exist_ok=True)

with open(os.path.join(TEMP_DIR, token, "flag.txt"), "w") as f:
    f.write(get_flag(token) + " ")

os.execvp(
    "kyzylborda-isolate",
    ["kyzylborda-isolate",
    "--ro-bind", f"{os.path.join(TEMP_DIR, token)}/flag.txt", "/app/flag.txt",
    "--ro-bind", BINARY, "/app/shout",
    "--chdir", "/app",
    "--tmpfs", "/tmp",
    "steam-run",
    "/app/shout"]
)
