#!/usr/bin/env python3

import os.path
import sys
import json
import hmac
import pickle
import random
import shutil
import subprocess
import tempfile

PREFIX = "ugra_wavy_obnoxious_squirrels_"
SECRET = b"shuat7Ooko6ee9oot"
SALT_SIZE = 8

LILYPOND_TEMPLATE = r"""
\include "english.ly"
\pointAndClickOff
\version "2.22.0"
#(set-default-paper-size "a4")

\header {
  title = "Symphony"
  composer = ""
  tagline = ""
  copyright = ""
}

\score {
  \new Staff \with { instrumentName = "Grand Piano" } {
    \tempo 4 = 1500
    r4 r4 r4 r4 r4 ^ \markup \italic { raccapricciante } r4 r4 r4
    +++
  }
}
"""

NOTE_NAMES = ["c,,,,,", "cs,,,,,", "d,,,,,", "ds,,,,,", "e,,,,,", "f,,,,,",
"fs,,,,,", "g,,,,,", "gs,,,,,", "a,,,,,", "as,,,,,", "b,,,,,", "c,,,,",
"cs,,,,", "d,,,,", "ds,,,,", "e,,,,", "f,,,,", "fs,,,,", "g,,,,", "gs,,,,",
"a,,,,", "as,,,,", "b,,,,", "c,,,", "cs,,,", "d,,,", "ds,,,", "e,,,", "f,,,",
"fs,,,", "g,,,", "gs,,,", "a,,,", "as,,,", "b,,,", "c,,", "cs,,", "d,,", "ds,,",
"e,,", "f,,", "fs,,", "g,,", "gs,,", "a,,", "as,,", "b,,", "c,", "cs,", "d,",
"ds,", "e,", "f,", "fs,", "g,", "gs,", "a,", "as,", "b,", "c", "cs", "d", "ds",
"e", "f", "fs", "g", "gs", "a", "as", "b", "c'", "cs'", "d'", "ds'", "e'", "f'",
"fs'", "g'", "gs'", "a'", "as'", "b'", "c''", "cs''", "d''", "ds''", "e''",
"f''", "fs''", "g''", "gs''", "a''", "as''", "b''", "c'''", "cs'''", "d'''",
"ds'''", "e'''", "f'''", "fs'''", "g'''", "gs'''", "a'''", "as'''", "b'''",
"c''''", "cs''''", "d''''", "ds''''", "e''''", "f''''", "fs''''", "g''''",
"gs''''", "a''''", "as''''", "b''''", "c'''''", "cs'''''", "d'''''", "ds'''''",
"e'''''", "f'''''", "fs'''''", "g'''''", "gs'''''", "a'''''"]

user_id = sys.argv[1]
target_dir = sys.argv[2]

flag = PREFIX + hmac.new(SECRET, user_id.encode(), "sha256").hexdigest()[:SALT_SIZE]
random.seed(hmac.new(SECRET, user_id.encode(), "sha256").digest())

attachments_dir = os.path.join(target_dir, "attachments")
os.makedirs(attachments_dir, exist_ok=True)

with tempfile.TemporaryDirectory() as temp_dir:
    notes = sum((pickle.load(open(os.path.join("private", "notes", f"{c}.pkl"), "rb")) for c in "-".join(flag)), [])

    lilypond_notes = ""

    for t, N in enumerate(notes):
        if sum(N) == 0:
            s = "r4"
        else:
            s = ""
            for f, n in enumerate(N):
                if "s" in NOTE_NAMES[f]:
                    continue  # so that it is not that scary
                if n ^ (random.random() < 0.005):
                    s += NOTE_NAMES[f] + " "
            s = f"<{s}>4"
        lilypond_notes += f"{s}\n"

    with open(os.path.join(temp_dir, "symphony.ly"), "w") as f:
        f.write(LILYPOND_TEMPLATE.replace("+++", lilypond_notes))

    subprocess.check_call(["lilypond", "symphony.ly"], cwd=temp_dir)

    shutil.copy(os.path.join(temp_dir, "symphony.pdf"), os.path.join(attachments_dir, "symphony.pdf"))

json.dump({"flags": [flag]}, sys.stdout)
