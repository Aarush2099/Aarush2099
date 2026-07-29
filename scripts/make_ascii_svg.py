#!/usr/bin/env python3
"""Convert a prepped photo into an animated ASCII portrait SVG.

Usage:
    python scripts/make_ascii_svg.py

Input:
    source-prepped.png
Output:
    aarush-ascii.svg
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

INPUT_NAME = "source-prepped.png"
OUTPUT_NAME = "aarush-ascii.svg"
RAMP = " .`:-=+*cs#%@"
COLUMNS = 100
ROWS = 53
FONT_SIZE = 12
CHAR_WIDTH = 10
LINE_HEIGHT = 14
PADDING = 10


def load_image(path: str) -> Image.Image:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing input image: {path}")
    with Image.open(path) as image:
        return image.convert("L")


def build_rows(image: Image.Image) -> list[str]:
    resized = image.resize((COLUMNS, ROWS), Image.LANCZOS)
    pixels = np.asarray(resized)
    rows: list[str] = []
    ramp_length = len(RAMP) - 1

    for y in range(ROWS):
        row_chars = []
        for x in range(COLUMNS):
            brightness = int(pixels[y, x])
            index = int((brightness * ramp_length) / 255)
            row_chars.append(RAMP[index])
        rows.append("".join(row_chars))

    return rows


def make_svg(rows: list[str], static: bool = False) -> str:
    width = COLUMNS * CHAR_WIDTH + PADDING * 2
    height = ROWS * LINE_HEIGHT + PADDING * 2
    full_text_width = COLUMNS * CHAR_WIDTH

    lines: list[str] = [
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {width} {height}\" width=\"{width}\" height=\"{height}\">",
        f"  <rect width=\"100%\" height=\"100%\" fill=\"transparent\" />",
        f"  <defs>",
    ]

    for index, _ in enumerate(rows):
        if static:
            continue
        lines.append(
            f"    <clipPath id=\"clip-row-{index}\" clipPathUnits=\"userSpaceOnUse\">"
        )
        lines.append(
            f"      <rect id=\"clip-row-rect-{index}\" x=\"{PADDING}\" y=\"{PADDING + index * LINE_HEIGHT - 10}\" width=\"0\" height=\"{LINE_HEIGHT}\">"
        )
        delay = round(index * 0.03, 3)
        lines.append(
            f"        <animate attributeName=\"width\" begin=\"{delay}s\" dur=\"0.55s\" values=\"0;{full_text_width}\" fill=\"freeze\" />"
        )
        lines.append("      </rect>")
        lines.append("    </clipPath>")

    lines.append("  </defs>")
    lines.append("  <g fill=\"#c9d1d9\" font-family=\"monospace\" font-size=\"12\">")

    for index, row in enumerate(rows):
        y = PADDING + (index + 1) * LINE_HEIGHT
        row_text = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if static:
            lines.append(
                f"    <text x=\"{PADDING}\" y=\"{y}\" xml:space=\"preserve\">{row_text}</text>"
            )
        else:
            lines.append(
                f"    <g clip-path=\"url(#clip-row-{index})\">"
            )
            lines.append(
                f"      <text x=\"{PADDING}\" y=\"{y}\" xml:space=\"preserve\">{row_text}</text>"
            )
            lines.append("    </g>")

    lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> int:
    static = os.getenv("STATIC") is not None
    try:
        image = load_image(INPUT_NAME)
        rows = build_rows(image)
        svg_text = make_svg(rows, static=static)
        Path(OUTPUT_NAME).write_text(svg_text, encoding="utf-8")
        print(f"Saved {OUTPUT_NAME}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
