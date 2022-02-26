#!/usr/bin/env python3

import base64
import hmac
import io
import json
import random
import subprocess
import sys
import tempfile

from dataclasses import dataclass
from pathlib import Path

import jinja2
  
from borb.pdf.document.document import Document  
from borb.pdf.page.page import Page  
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout  
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout  
from borb.pdf.canvas.layout.text.paragraph import Paragraph  
from borb.pdf.pdf import PDF  
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont  
from borb.pdf.canvas.font.font import Font

from PIL import Image, ImageDraw, ImageFont

UNICODE_RANGES = [
    # [0x0020, 0x007F],
    [0x00A0, 0x074F],
    [0x0780, 0x07BF],
    [0x0900, 0x137F],
    [0x13A0, 0x18AF],
    [0x1900, 0x197F],
    [0x19E0, 0x19FF],
    [0x1D00, 0x1D7F],
    [0x1E00, 0x2BFF],
    [0x2E80, 0x2FDF],
    [0x2FF0, 0x31BF],
    [0x31F0, 0xA4CF],
    [0xAC00, 0xD7AF],
    [0xF900, 0xFE0F],
    [0xFE20, 0xFFEF]
]

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz=_"

TASKS = [
    "cmap1",
    "cmap2"
]

PREFIX = [
    "ugra_you_do_not_need_usepackage_cmap_",
    "ugra_oh_what_a_weird_font_here_"
]

FLAG_SECRET = [
    b"resolution-appearance-orientation-dangerous-experiment",
    b"underline-basketball-executive-refrigerator-inhabitant"
]
FLAG_SALT_SIZE = 12

@dataclass
class Character:
    name: str
    position: int
    code: int
    data: str


def name(code: int):
    return "uni" + ("0000" + hex(code).upper()[2:])[-4:]



def get_flag(i, token):
    return PREFIX[i] + hmac.new(FLAG_SECRET[i], token.encode(), "sha256").hexdigest()[:FLAG_SALT_SIZE]


def generate():
    if len(sys.argv) != 4:
        print("Usage: generate.py user_id target_dir tasks", file=sys.stderr)
        sys.exit(1)

    user_id = sys.argv[1]
    flag_for_picture = get_flag(0, user_id)
    flag_for_font = get_flag(1, user_id)

    # Generate image with flag1

    image = Image.new(
        "RGB",
        (1337, 100),
        color=("#a7d20c")
    )
    image_font = ImageFont.truetype("NotoSansMono-Regular.ttf", size=40)
    drawer = ImageDraw.Draw(image)
    drawer.text(
        (70, 25),
        flag_for_picture,
        font=image_font,
        fill='#8a86ca'
    )
    
    image_stream = io.BytesIO()
    image.save(image_stream, format="PNG")

    content = base64.b32encode(image_stream.getvalue()).decode()

    with tempfile.TemporaryDirectory() as temp_dir:
        rnd = random.Random(f"{user_id}-fefo-fifa-fafi")

        private = Path(__file__).parent / "private"
        trash = Path(temp_dir)
        destination = Path(sys.argv[2])

        # Generate font description for flag2 and for encoding image

        generated = "aa"
        while len(set(generated)) != len(generated):
            generated = [
                rnd.randint(*rnd.choice(UNICODE_RANGES))
                for _ in ALPHABET
            ]

        translation = str.maketrans(
            ALPHABET,
            ''.join(map(chr, generated))
        )

        chars = []
        for char, code in zip(ALPHABET, generated):
            with (private / "characters" / f"{ord(char)}").open() as char_data:
                chars.append(Character(
                    name(code),
                    code,
                    code,
                    char_data.read()
                ))
        
        for code, char in enumerate(flag_for_font, start=65537):
            with (private / "characters" / f"{ord(char)}").open() as char_data:
                chars.append(Character(
                    f"add{code}",
                    code,
                    -1,
                    char_data.read()
                ))

        with (private / "monplesir.sfd").open() as template_file, \
             (trash / "result.sfd").open("w") as output:
            template = jinja2.Template(template_file.read())
            output.write(template.render(
                max_char=65537+len(flag_for_font),
                chars=chars,
                enumerate=enumerate
            ))

        # Generate TTF
        result = subprocess.run(
            [
                "/usr/bin/fontforge",
                "--appimage-extract-and-run",
                "-c",
                "open(argv[1]).generate(argv[2])",
                str(trash / "result.sfd"),
                str(trash / "font.ttf")
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            print(f"Cannot generate font, code {result.returncode}", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        # Apply it to PDF
        pdf = Document()

        page = Page()
        pdf.append_page(page)
    
        layout = SingleColumnLayout(page)
        pdf_font = TrueTypeFont.true_type_font_from_file(trash / "font.ttf")

        for idx in range(0, len(content), 25):
            layout.add(Paragraph(
                content[idx:idx+25].translate(translation),
                font=pdf_font,
                font_size=18
            ))
        
        (destination / "attachments").mkdir(parents=True, exist_ok=True)
        with (destination / "attachments" / "flag.pdf").open("wb") as pdf_file:
            PDF.dumps(pdf_file, pdf)

    json.dump({
        TASKS[i]: {
            "flags": [get_flag(i, user_id)],
            "substitutions": {}
        }
        for i in range(len(TASKS))
    }, sys.stdout)


if __name__ == "__main__":
    generate()

