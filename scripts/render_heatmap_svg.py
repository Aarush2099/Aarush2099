#!/usr/bin/env python3
"""Render a GitHub contribution heatmap SVG from contributions JSON.

Usage:
    python scripts/render_heatmap_svg.py

Input:
    data/contributions.json
Output:
    contrib-heatmap.svg
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

INPUT_PATH = Path("data") / "contributions.json"
OUTPUT_NAME = "contrib-heatmap.svg"
CELL_SIZE = 12
CELL_GAP = 4
MARGIN = 20
TITLE_HEIGHT = 28
LEGEND_BOX = 10
LEGEND_GAP = 6
PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


def load_data(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing contributions JSON: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def map_level(count: int, max_count: int) -> int:
    if count <= 0 or max_count <= 0:
        return 0
    level = 1 + int((count - 1) * 4 / max(1, max_count - 1))
    return min(5, max(1, level))


def build_svg(data: dict, static: bool = False) -> str:
    days = data["days"]
    max_count = max((day["count"] for day in days), default=0)
    week_count = max((day["week_index"] for day in days), default=52) + 1
    width = MARGIN * 2 + week_count * (CELL_SIZE + CELL_GAP) - CELL_GAP
    height = MARGIN * 2 + TITLE_HEIGHT + 7 * (CELL_SIZE + CELL_GAP) - CELL_GAP + 60

    lines: list[str] = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {width} {height}\" width=\"{width}\" height=\"{height}\">",
        "  <style type=\"text/css\">",
        "    .label { font: 12px monospace; fill: #c9d1d9; }",
        "    .footer { font: 12px monospace; fill: #8b949e; }",
        "  </style>",
        "  <rect width=\"100%\" height=\"100%\" rx=\"20\" fill=\"#0d1117\" />",
        f"  <text x=\"{MARGIN}\" y=\"{MARGIN + 14}\" class=\"label\">GitHub contributions · {data.get('username', '')}</text>",
    ]

    for day in days:
        week_index = day["week_index"]
        weekday_index = day["weekday_index"]
        count = day["count"]
        level = map_level(count, max_count)
        color = PALETTE[level]
        x = MARGIN + week_index * (CELL_SIZE + CELL_GAP)
        y = MARGIN + TITLE_HEIGHT + weekday_index * (CELL_SIZE + CELL_GAP)
        delay = round((week_index + weekday_index) * 0.01, 3)

        lines.append(
            f"  <rect x=\"{x}\" y=\"{y}\" width=\"{CELL_SIZE}\" height=\"{CELL_SIZE}\" rx=\"3\" fill=\"{color}\" opacity=\"{0 if not static else 1}\" >"
        )
        if not static:
            lines.append(
                f"    <animate attributeName=\"opacity\" from=\"0\" to=\"1\" begin=\"{delay}s\" dur=\"0.30s\" fill=\"freeze\" />"
            )
            lines.append(
                f"    <animate attributeName=\"y\" from=\"{y - 6}\" to=\"{y}\" begin=\"{delay}s\" dur=\"0.30s\" fill=\"freeze\" />"
            )
        lines.append("  </rect>")

    legend_x = width - MARGIN - (LEGEND_BOX + LEGEND_GAP) * 6
    legend_y = MARGIN + TITLE_HEIGHT + 7 * (CELL_SIZE + CELL_GAP) + 16
    lines.append(f"  <text x=\"{legend_x}\" y=\"{legend_y}\" class=\"label\">Less</text>")
    for index, color in enumerate(PALETTE):
        box_x = legend_x + 38 + index * (LEGEND_BOX + LEGEND_GAP)
        lines.append(
            f"  <rect x=\"{box_x}\" y=\"{legend_y - LEGEND_BOX + 4}\" width=\"{LEGEND_BOX}\" height=\"{LEGEND_BOX}\" rx=\"2\" fill=\"{color}\" />"
        )
    lines.append(
        f"  <text x=\"{legend_x + 38 + (LEGEND_BOX + LEGEND_GAP) * 6 - 4}\" y=\"{legend_y}\" class=\"label\">More</text>"
    )

    footer_y = legend_y + 24
    stats = (
        f"{data.get('total', 0)} contributions in the last year · "
        f"current streak {data.get('current_streak', 0)} days · "
        f"longest streak {data.get('longest_streak', 0)} days · "
        f"best day {data.get('best_day', {}).get('count', 0)} contributions"
    )
    lines.append(f"  <text x=\"{MARGIN}\" y=\"{footer_y}\" class=\"footer\">{stats}</text>")
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> int:
    static = os.getenv("STATIC") is not None
    try:
        data = load_data(INPUT_PATH)
        svg_text = build_svg(data, static=static)
        Path(OUTPUT_NAME).write_text(svg_text, encoding="utf-8")
        print(f"Saved {OUTPUT_NAME}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
