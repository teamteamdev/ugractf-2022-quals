#!/usr/bin/env python3

import os.path
import os
import sys
import json
import hmac
import random
import shutil
import subprocess
import tempfile
import io
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
from jinja2 import Environment, FileSystemLoader


PREFIX = "ugra_kerckhoffs_saw_disassemblers_coming_"
SECRET = b"t3_L{:gh1jg98"
SALT_SIZE = 8

user_id = sys.argv[1]
target_dir = sys.argv[2]

flag = PREFIX + hmac.new(SECRET, user_id.encode(), "sha256").hexdigest()[:SALT_SIZE]
random.seed(hmac.new(SECRET, user_id.encode(), "sha256").digest())

JINJA_ENV = Environment(loader=FileSystemLoader('private'))
C_TEMPLATE = JINJA_ENV.get_template('program.c')

random.seed('NIX_FLAKES_RULE!')

def generate_masks(count):
    template = [0xff] * 2 + [0x00] * 2
    masks = [int.from_bytes(random.sample(template, 4), 'big') for _ in range(count)]
    return masks


MASKS = generate_masks(32)

FONT = PIL.ImageFont.load(os.path.join('private', 'Galmuri11-Bold.pil'))
TEMPLATE = PIL.Image.open(os.path.join('private', 'template.gif'))


def generate_image(text='ugra_kerckhoffs_saw_disassemblers_coming_3493f0ce89'):
    text_size = FONT.getsize(text)
    image = PIL.Image.new("RGB", (text_size[0], 140))
    image.paste(TEMPLATE, (text_size[0] // 2 - TEMPLATE.size[0] // 2, 0))
    draw = PIL.ImageDraw.ImageDraw(image)
    draw.text((0, 140-13), text, font=FONT, fill=(200, 100, 0))

    image_bytes = io.BytesIO()
    image.save(image_bytes, format="gif", optimize=True)
    #sys.stdout.buffer.write(image_bytes.getvalue())
    return image_bytes.getvalue()


def generate_gamma(image):
    gamma_bytes = random.randbytes(len(image))
    return gamma_bytes


def encrypt(image, gamma):
    encrypted = bytes(c ^ g for c, g in zip(image, gamma))
    return encrypted


def mix(encrypted, gamma):
    mix = b''
    for i in range(0, len(encrypted), 4):
        g_bytes = int.from_bytes(gamma[i:i+4], 'big')
        e_bytes = int.from_bytes(encrypted[i:i+4], 'big')
        mask = MASKS[i // 4 % 32]
        mix_a = (g_bytes &  mask) | (e_bytes & ~mask)
        mix_b = (g_bytes & ~mask) | (e_bytes &  mask)
        mix += mix_a.to_bytes(4, 'big') + mix_b.to_bytes(4, 'big')
    return mix


def prepare_c_source(masks, mix):
    c_masks = f'{{{",".join(str(x) + "u" for x in masks)}}}'
    c_mix = f'{{{",".join(hex(x) for x in mix)}}}'
    source = C_TEMPLATE.render(
        masks=c_masks,
        mix=c_mix
    )
    return source


attachments_dir = os.path.join(target_dir, "attachments")
os.makedirs(attachments_dir, exist_ok=True)

with tempfile.TemporaryDirectory() as temp_dir:
    image = generate_image(flag)
    gamma = generate_gamma(image)
    encrypted = encrypt(image, gamma)
    mixed = mix(gamma, encrypted)


    with open(os.path.join(temp_dir, "program.c"), "w") as f:
        f.write(prepare_c_source(MASKS, mixed))

    x = subprocess.check_call(
        ["gcc", "program.c", "-oprogram", "-Os", "-s", "-ludev", "-fno-stack-protector", "-zexecstack", "-no-pie"],
        cwd=temp_dir
    )

    print(x, temp_dir)

    shutil.copy(os.path.join(temp_dir, "program"), os.path.join(attachments_dir, "anft_viewer_PRE-RELEASE"))

json.dump({"flags": [flag]}, sys.stdout)
