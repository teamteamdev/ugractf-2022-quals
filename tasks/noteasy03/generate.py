#!/usr/bin/env python3

import base64
import hmac
import io
import json
import random
import subprocess
import sys
import tempfile

from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
import PyECCArithmetic as ec
from matplotlib import pyplot as plt
from matplotlib.text import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

matplotlib.use('agg')
plt.style.use('dark_background')
plt.rcParams.update({"figure.facecolor": "#201f35"})
fp = FontProperties(family="monospace")

PREFIX = "ugra_in_case_of_losing_your_sanity_dial_oh_three_"
FLAG_SECRET = b"0etoelliptika3etokuba03etosamiznaete"
FLAG_SALT_SIZE = 21
b, r = 0, 31


def get_flag(token):
    salt = [chr(i % 16 + ord('A')) for i in hmac.new(FLAG_SECRET, token.encode(), "sha512").digest()]
    return PREFIX + ''.join(salt)[:FLAG_SALT_SIZE].lower()


def fig_to_img(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, facecolor="#201f35")
    buffer.seek(0)
    return Image.open(buffer)


def plot(alphabet):
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.tight_layout(pad=0.1)
    ax.set_facecolor("#201f35")

    ax.set_xlim(-1, 31)
    ax.set_ylim(-17, 17)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))

    y, x = np.mgrid[-32:32:1500j, -32:32:1500j]
    plt.contour(x, y, np.mod(np.power(y, 2) - np.power(x, 3) - x - 0, 31), alpha=0.15)

    for letter, point in alphabet.items():
        label = TextPath((5,5), letter.upper(), prop=fp, size=20)
        ax.plot(point.x, point.y, marker='o', ms=3, color='#A7D20C')
        ax.plot(point.x, point.y, marker=label, ms=25, color='#A7D20C')

    ax.grid(which='major', color='#ffffff', linestyle='--')

    return fig_to_img(fig)


def encrypt(flag, alphabet):
    ciphertext = []
    for char in flag.upper():
        point = alphabet[char] * 3
        if point.y >= 16:
            point.y -= r
        ciphertext.extend([c for c, p in alphabet.items() if point == p])
    return ''.join(ciphertext).lower()


A_VALUES = range(-10, 10)


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    flag = get_flag(user_id)

    random.seed(user_id)
    a = random.choice(A_VALUES)
    curve = ec.Curve(a, b, r)
    points = []

    for i in range(31):
        for j in range(31):
            point = ec.Point(i, j, curve=curve)
            if point.isOnCurve:
                if point.y >= 16:
                    point.y -= r
                points.append(point)

    alphabet = {chr(ord('A') + i): p for i, p in enumerate(points)}
    plot_img = plot(alphabet)
    ciphertext = encrypt(flag, alphabet)


    with tempfile.TemporaryDirectory() as temp_dir:
        trash = Path(temp_dir)
        destination = Path(sys.argv[2])

        (destination / "attachments").mkdir(parents=True, exist_ok=True)
        (destination / "static").mkdir(parents=True, exist_ok=True)

        with (destination / "attachments" / "ciphertext.txt").open("w") as ciphertext_file:
            ciphertext_file.write(ciphertext)

        plot_img.save((destination / "static" / "alphabet.png"))



    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
