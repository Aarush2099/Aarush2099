#!/usr/bin/env python3
"""Fetch GitHub contributions and serialize a 53×7 grid into JSON.

Usage:
    python scripts/fetch_contributions.py

Output:
    data/contributions.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Aarush2099"
OUTPUT_PATH = Path("data") / "contributions.json"
CONTRIBUTIONS_URL = f"https://github.com/users/{USERNAME}/contributions"
DATE_FORMAT = "%Y-%m-%d"


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "User-Agent": "github-profile-readme-generator/1.0",
            "Accept": "text/html",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.text


def parse_data_cells(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    cells = []

    for element in soup.find_all(attrs={"data-date": True}):
        date_text = element.get("data-date")
        if not date_text:
            continue

        count_text = element.get("data-count") or element.get("aria-label") or "0"
        match = re.search(r"(\d+)", str(count_text))
        count = int(match.group(1)) if match else 0

        cells.append({"date": date_text, "count": count})

    if not cells:
        raise ValueError("Could not find contribution cells in GitHub HTML.")

    return cells


def compute_day_grid(rows: list[dict[str, str]]) -> list[dict]:
    parsed = [
        {
            "date": datetime.strptime(row["date"], DATE_FORMAT).date(),
            "count": int(row["count"]),
        }
        for row in rows
    ]
    parsed.sort(key=lambda entry: entry["date"])

    first_date = parsed[0]["date"]
    start_sunday = first_date - timedelta(days=(first_date.weekday() + 1) % 7)

    day_grid: list[dict] = []
    for entry in parsed:
        delta = entry["date"] - start_sunday
        weekday_index = (entry["date"].weekday() + 1) % 7
        week_index = delta.days // 7
        day_grid.append(
            {
                "date": entry["date"].isoformat(),
                "count": entry["count"],
                "week_index": week_index,
                "weekday_index": weekday_index,
            }
        )

    return day_grid


def compute_streaks(days: list[dict]) -> tuple[int, int]:
    current = 0
    longest = 0
    running = 0

    for day in days:
        if day["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    for day in reversed(days):
        if day["count"] > 0:
            current += 1
        else:
            break

    return current, longest


def compute_monthly_totals(days: list[dict]) -> OrderedDict[str, int]:
    monthly: OrderedDict[str, int] = OrderedDict()

    for day in days:
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]

    return monthly


def main() -> int:
    try:
        html = fetch_html(CONTRIBUTIONS_URL)
        raw_cells = parse_data_cells(html)
        days = compute_day_grid(raw_cells)

        total = sum(day["count"] for day in days)
        current_streak, longest_streak = compute_streaks(days)
        best_day = max(days, key=lambda entry: entry["count"])
        monthly_totals = compute_monthly_totals(days)

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
            json.dump(
                {
                    "username": USERNAME,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "total": total,
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "best_day": best_day,
                    "monthly_totals": monthly_totals,
                    "days": days,
                },
                output_file,
                indent=2,
            )

        print(f"Saved {OUTPUT_PATH}")
        return 0
    except requests.RequestException as exc:
        print(f"Network error fetching contributions: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
