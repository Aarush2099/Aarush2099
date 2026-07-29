#!/usr/bin/env python3
"""Render an animated neofetch-style info card SVG.

Usage:
    python scripts/make_info_card.py

Output:
    info-card.svg
"""

from __future__ import annotations

import os
from pathlib import Path

OUTPUT_NAME = "info-card.svg"
CARD_WIDTH = 490
CARD_HEIGHT = 360
TITLE_HEIGHT = 42
INNER_MARGIN = 24
LABEL_COLOR = "#56d6ff"
TEXT_COLOR = "#c9d1d9"
BACKGROUND_COLOR = "#0b1220"
PANEL_COLOR = "#010409"
TITLE_BAR_COLOR = "#161b22"
LABEL_FONT_SIZE = 12
VALUE_FONT_SIZE = 12
TITLE_FONT_SIZE = 14
ROW_SPACING = 28
BASE_Y = TITLE_HEIGHT + INNER_MARGIN

ROWS = [
    ("Now", "BTech CSE @ Manipal University Jaipur"),
    (
        "Prev",
        "Hackathons (Hack for Humanity), Student club president, community projects",
    ),
    (
        "Stack",
        "Python · JavaScript · TypeScript · React · Node.js · Flask · GitHub · Cloud (GCP/AWS)",
    ),
    (
        "Highlights",
        "SightCom (AI accessibility app) · Hackathons & dev sprints · Competitive programming & open-source contributions",
    ),
]


def chunk_text(text: str, max_chars: int = 46) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = []

    for word in words:
        if sum(len(part) for part in current) + len(current) + len(word) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))

    return lines


def build_card(static: bool = False) -> str:
    lines: list[str] = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {CARD_WIDTH} {CARD_HEIGHT}\" width=\"{CARD_WIDTH}\" height=\"{CARD_HEIGHT}\">",
        f"  <rect width=\"100%\" height=\"100%\" rx=\"24\" fill=\"{BACKGROUND_COLOR}\" />",
        f"  <rect x=\"0\" y=\"0\" width=\"{CARD_WIDTH}\" height=\"{TITLE_HEIGHT}\" rx=\"24\" fill=\"{TITLE_BAR_COLOR}\" />",
        f"  <text x=\"{INNER_MARGIN}\" y=\"{TITLE_HEIGHT - 12}\" fill=\"{LABEL_COLOR}\" font-family=\"monospace\" font-size=\"{TITLE_FONT_SIZE}\">",
        "    aarush@github",
        "  </text>",
    ]

    current_y = BASE_Y
    animation_delay = 0.15

    for index, (label, value) in enumerate(ROWS):
        label_x = INNER_MARGIN
        value_x = INNER_MARGIN
        label_y = current_y
        value_lines = chunk_text(value, max_chars=46)
        group_id = f"row-{index}"
        begin = f"{index * animation_delay:.2f}s"

        if static:
            lines.append(
                f"  <text x=\"{label_x}\" y=\"{label_y}\" fill=\"{LABEL_COLOR}\" font-family=\"monospace\" font-size=\"{LABEL_FONT_SIZE}\">{label}</text>"
            )
        else:
            lines.append(
                f"  <g opacity=\"0\" transform=\"translate(0, 10)\">"
            )
            lines.append(
                f"    <animate attributeName=\"opacity\" from=\"0\" to=\"1\" begin=\"{begin}\" dur=\"0.35s\" fill=\"freeze\" />"
            )
            lines.append(
                f"    <animateTransform attributeName=\"transform\" attributeType=\"XML\" type=\"translate\" from=\"0 10\" to=\"0 0\" begin=\"{begin}\" dur=\"0.35s\" fill=\"freeze\" />"
            )
            lines.append("    <text x=\"{label_x}\" y=\"{label_y}\" fill=\"{LABEL_COLOR}\" font-family=\"monospace\" font-size=\"{LABEL_FONT_SIZE}\">{label}</text>".format(label_x=label_x, label_y=label_y, LABEL_COLOR=LABEL_COLOR, LABEL_FONT_SIZE=LABEL_FONT_SIZE, label=label))
        
        if static:
            pass
        else:
            lines.append("  </g>")

        current_y += ROW_SPACING
        for line in value_lines:
            if static:
                lines.append(
                    f"  <text x=\"{value_x}\" y=\"{current_y}\" fill=\"{TEXT_COLOR}\" font-family=\"monospace\" font-size=\"{VALUE_FONT_SIZE}\">{line}</text>"
                )
            else:
                lines.append(
                    f"  <g opacity=\"0\" transform=\"translate(0, 10)\">"
                )
                lines.append(
                    f"    <animate attributeName=\"opacity\" from=\"0\" to=\"1\" begin=\"{begin}\" dur=\"0.35s\" fill=\"freeze\" />"
                )
                lines.append(
                    f"    <animateTransform attributeName=\"transform\" attributeType=\"XML\" type=\"translate\" from=\"0 10\" to=\"0 0\" begin=\"{begin}\" dur=\"0.35s\" fill=\"freeze\" />"
                )
                lines.append(
                    f"    <text x=\"{value_x}\" y=\"{current_y}\" fill=\"{TEXT_COLOR}\" font-family=\"monospace\" font-size=\"{VALUE_FONT_SIZE}\">{line}</text>"
                )
                lines.append("  </g>")
            current_y += 18
        current_y += 8

    lines.append("</svg>")
    return "\n".join(lines)


def main() -> int:
    static = os.getenv("STATIC") is not None
    content = build_card(static=static)
    Path(OUTPUT_NAME).write_text(content, encoding="utf-8")
    print(f"Saved {OUTPUT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
