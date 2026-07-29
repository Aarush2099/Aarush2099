#!/usr/bin/env python3
"""Prepare a profile photo for ASCII portrait generation.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Output:
    source-prepped.png
"""

from __future__ import annotations

import argparse
import io
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUTPUT_NAME = "source-prepped.png"
MAX_WIDTH = 1200
MAX_HEIGHT = 640


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a photo for ASCII portrait generation."
    )
    parser.add_argument(
        "input_path",
        help="Path to the source photo file.",
    )
    return parser.parse_args()


def load_source_image(path: str) -> Image.Image:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    try:
        image = Image.open(path)
        return image.convert("RGBA")
    except OSError as exc:
        raise ValueError(f"Could not open image '{path}': {exc}") from exc


def remove_background(image: Image.Image) -> Image.Image:
    with io.BytesIO() as input_buffer:
        image.save(input_buffer, format="PNG")
        input_buffer.seek(0)
        result_bytes = remove(input_buffer.read())
    with io.BytesIO(result_bytes) as output_buffer:
        return Image.open(output_buffer).convert("RGBA")


def resize_with_padding(image: Image.Image, width: int, height: int) -> Image.Image:
    image_copy = image.copy()
    image_copy.thumbnail((width, height), Image.LANCZOS)

    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    paste_x = (width - image_copy.width) // 2
    paste_y = (height - image_copy.height) // 2
    canvas.paste(image_copy, (paste_x, paste_y), image_copy)
    return canvas


def apply_clahe(image: Image.Image) -> Image.Image:
    grayscale = image.convert("L")
    array = np.asarray(grayscale)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(array)
    return Image.fromarray(enhanced)


def compose_white_background(image: Image.Image) -> Image.Image:
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(background, image)
    return composited.convert("L")


def main() -> int:
    args = parse_args()
    source_path = args.input_path

    try:
        source = load_source_image(source_path)
        subject = remove_background(source)
        padded = resize_with_padding(subject, MAX_WIDTH, MAX_HEIGHT)
        prepped = compose_white_background(padded)
        final_image = apply_clahe(prepped)
        final_image.save(OUTPUT_NAME)
        print(f"Saved {OUTPUT_NAME}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
