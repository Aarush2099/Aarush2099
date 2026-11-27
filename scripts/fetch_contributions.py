#!/usr/bin/env python3
"""Fetch GitHub contribution data and write the profile-card data file."""

import datetime
import json
import os
import re

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_PROFILE_USER", "Aarush2099")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ROOT, "data", "contributions.json")


def fetch_days():
    url = "https://github.com/users/{}/contributions".format(USER)
    response = requests.get(
        url,
        headers={"User-Agent": "profile-art/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tooltips = {
        tooltip.get("for"): tooltip.get_text(" ", strip=True)
        for tooltip in soup.select("tool-tip")
    }

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        day_date = cell.get("data-date")
        if not day_date:
            continue
        tooltip = tooltips.get(cell.get("id"), "")
        first_word = tooltip.split()[0].replace(",", "") if tooltip else ""
        count = int(first_word) if re.fullmatch(r"\d+", first_word) else 0
        days.append({"date": day_date, "count": count})

    if not days:
        raise RuntimeError("No contribution calendar days found in GitHub HTML")
    days.sort(key=lambda day: day["date"])
    return days[-365:]


def streaks(days, today):
    counts = {day["date"]: day["count"] for day in days}
    yesterday = today - datetime.timedelta(days=1)
    streak_date = today if counts.get(today.isoformat(), 0) > 0 else yesterday
    current = 0
    while counts.get(streak_date.isoformat(), 0) > 0:
        current += 1
        streak_date -= datetime.timedelta(days=1)

    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)
    return current, longest


def build_data(days, today):
    if not days:
        raise ValueError("At least one contribution day is required")
    total = sum(day["count"] for day in days)
    active_days = sum(day["count"] > 0 for day in days)
    current, longest = streaks(days, today)
    best = max(days, key=lambda day: (day["count"], day["date"]))

    month_totals = {}
    for day in days:
        key = day["date"][:7]
        month_totals[key] = month_totals.get(key, 0) + day["count"]
    monthly = [
        {"month": month, "total": count}
        for month, count in sorted(month_totals.items())[-12:]
    ]
    card_months = [
        {
            "label": datetime.date.fromisoformat(item["month"] + "-01").strftime("%b"),
            "count": item["total"],
        }
        for item in monthly
    ]

    return {
        "username": USER,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "total": total,
        "active_days": active_days,
        "current_streak": {"length": current},
        "longest_streak": {"length": longest},
        "streak": current,
        "best_day": best,
        "busiest": best,
        "monthly": monthly,
        "months": card_months,
        "days": days,
    }


def main():
    today = datetime.date.today()
    days = fetch_days()
    data = build_data(days, today)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as output:
        json.dump(data, output, indent=2)
        output.write("\n")
    print(
        "Wrote {}: {} contributions, {} day current streak".format(
            os.path.normpath(OUTPUT_PATH),
            data["total_contributions"],
            data["current_streak"]["length"],
        )
    )


if __name__ == "__main__":
    main()
