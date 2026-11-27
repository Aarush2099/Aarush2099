#!/usr/bin/env python3
"""Render animated, self-contained profile cards into cards/."""

import base64
import datetime
import json
import os
from html import escape as html_escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "contributions.json")
CARDS_PATH = os.path.join(ROOT, "cards")
FONTS_PATH = os.path.join(ROOT, "fonts")
STATIC = os.environ.get("STATIC") == "1"

NAME_FIRST = "Aarush"
NAME_LAST = "Mahajan"
HERO_LINE_1 = "Computer Science (B.Tech) at Manipal University Jaipur"
HERO_LINE_2 = "TKS Innovate Student"

PAPER = "#f3f3f1"
PAPER_DEEP = "#e2e2de"
INK = "#111111"
INK_SOFT = "#3a3a3c"
MUTED = "#6e6e73"
RULE = "#dcdcd7"
BLUE = "#2f55ff"
RED = "#ef3b2d"
YELLOW = "#ffc81a"
WHITE = "#ffffff"
W = 880

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "'Geist', Arial, sans-serif"
MONO = "'Geist Mono', monospace"

FONT_DEFS = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

ANIMATION_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.1)}100%{opacity:1;transform:none}}
@keyframes tilein{0%{opacity:0;transform:translateY(60px) scale(.7) rotate(-6deg)}60%{opacity:1;transform:translateY(-6px) scale(1.03) rotate(1.5deg)}100%{opacity:1;transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}30%,100%{transform:translateX(420px) skewX(-20deg)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.t{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.t{animation:none!important;opacity:1!important;transform:none!important}.sh{display:none!important}}
"""

TILES = [
    ("build", "BUILD", BLUE, WHITE, "6 picks",
     "Software, simulations, and AI tools.", 3.1),
    ("explore", "EXPLORE", RED, WHITE, "TKS",
     "Exploring ideas through TKS Innovate.", 3.35),
    ("learn", "LEARN", YELLOW, INK, "Student",
     HERO_LINE_1, 3.6),
]

REPOS = [
    ("tks", "TKS-Create-Aegis-Orbit",
     "Research prototype for satellite conjunction simulations.",
     "Python", BLUE),
    ("create", "Pgc2", "TypeScript web app with a Supabase backend.",
     "TypeScript", RED),
    ("aegis", "Tactile-Text",
     "Flutter app for accessible digital Braille.",
     "Dart", YELLOW),
    ("orbit", "SightCom",
     "AI-assisted app that helps blind users access visual information.",
     "Dart", BLUE),
    ("carbonconversations", "Digital-Farmer",
     "AI leaf-disease detection with treatment recommendations.",
     "Python", RED),
    ("pgcapril", "Teens-In-AI-Verdant-Green",
     "AI-powered microclimate planner for carbon sequestration.",
     "TypeScript", YELLOW),
]


def escape(value, quote=True):
    return html_escape(str(value), quote=quote)


def font_css(keys):
    rules = []
    for key in keys:
        family, style, weight, filename = FONT_DEFS[key]
        with open(os.path.join(FONTS_PATH, filename), "rb") as font_file:
            encoded = base64.b64encode(font_file.read()).decode("ascii")
        rules.append(
            "@font-face{{font-family:'{}';font-style:{};font-weight:{};"
            "src:url(data:font/woff;base64,{}) format('woff')}}".format(
                family, style, weight, encoded
            )
        )
    return "".join(rules)


def svg(width, height, body, label, fonts, background=PAPER):
    styles = font_css(fonts)
    if not STATIC:
        styles += ANIMATION_CSS
    title = escape(label, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" '
        'viewBox="0 0 {} {}" role="img" aria-label="{}">'
        '<title>{}</title><rect width="100%" height="100%" rx="14" '
        'fill="{}"/><style>{}</style>{}</svg>'
    ).format(width, height, width, height, title, title, background, styles, body)


def write_card(filename, contents):
    os.makedirs(CARDS_PATH, exist_ok=True)
    with open(os.path.join(CARDS_PATH, filename), "w", encoding="utf-8") as output:
        output.write(contents)
    print("wrote cards/{}".format(filename))


def delay(seconds):
    return 'style="animation-delay:{:.2f}s"'.format(seconds)


def text(x, y, value, family, size, fill, class_name="r", at=0.0, extra=""):
    class_attr = 'class="{}" '.format(class_name) if class_name else ""
    timing = delay(at) if class_name else ""
    return (
        '<text {}{} x="{}" y="{}" font-family="{}" font-size="{}" '
        'fill="{}" {}>{}</text>'
    ).format(class_attr, timing, x, y, family, size, fill, extra, value)


def wrap(value, limit):
    lines = []
    line = ""
    for word in value.split():
        if line and len(line) + len(word) + 1 > limit:
            lines.append(line)
            line = word
        else:
            line = "{} {}".format(line, word).strip()
    if line:
        lines.append(line)
    return lines


def hero_card():
    height = 360
    body = """
<rect width="{width}" height="{height}" rx="14" fill="{paper}"/>
<g class="f" {first_delay}>
  <rect x="44" y="46" width="8" height="8" rx="2" fill="{blue}"/>
  {profile_line}
</g>
{first_name}
{last_name}
{student_line}
""".format(
        width=W,
        height=height,
        paper=PAPER,
        first_delay=delay(0),
        blue=BLUE,
        profile_line=text(
            62, 54, escape(HERO_LINE_1), MONO, 12, MUTED, class_name="",
            extra='letter-spacing="1"',
        ),
        first_name=text(
            44, 170, escape(NAME_FIRST), SERIF, 116, INK, at=0.15,
            extra='letter-spacing="-2.5"',
        ),
        last_name=text(
            44, 270, escape(NAME_LAST), SERIF, 116, INK, at=0.3,
            extra='font-style="italic" letter-spacing="-2.5"',
        ),
        student_line=text(
            48, 318, escape(HERO_LINE_2), SANS, 18, INK_SOFT, at=0.55,
        ),
    )
    write_card(
        "hero.svg",
        svg(
            W, height, body,
            "{} {}. {}. {}.".format(
                NAME_FIRST, NAME_LAST, HERO_LINE_1, HERO_LINE_2
            ),
            ["serif", "serif-i", "sans", "mono"],
        ),
    )


def tile_card(name, label, colour, text_colour, value, blurb, start_delay):
    width = W / 3
    height = 200
    lines = wrap(blurb, 34)
    description = "".join(
        text(
            22, 150 + index * 20, escape(line), SANS, 14, text_colour,
            at=start_delay + 0.75 + index * 0.1, extra='opacity=".92"',
        )
        for index, line in enumerate(lines)
    )
    body = """
<defs>
  <clipPath id="card-{name}"><rect width="{width:.1f}" height="{height}" rx="14"/></clipPath>
  <linearGradient id="gl-{name}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="t" {tile_delay}>
  <g clip-path="url(#card-{name})">
    <rect width="{width:.1f}" height="{height}" fill="{colour}"/>
    <rect class="sh" style="animation-delay:{sheen_delay:.2f}s" x="0" y="-20" width="90" height="{sheen_height}" fill="url(#gl-{name})" transform="translate(-260 0)"/>
  </g>
  {label_text}
  {value_text}
  {description}
</g>
""".format(
        name=name,
        width=width,
        height=height,
        tile_delay=delay(start_delay),
        colour=colour,
        sheen_delay=start_delay + 1.4,
        sheen_height=height + 40,
        label_text=text(
            22, 38, escape(label), MONO, 12, text_colour, class_name="",
            extra='letter-spacing="1.2"',
        ),
        value_text=text(
            22, 112, escape(value), SERIF, 44, text_colour,
            at=start_delay + 0.45,
        ),
        description=description,
    )
    write_card(
        "{}.svg".format(name),
        svg(
            round(width, 2), height, body,
            "{}: {}. {}".format(label, value, blurb),
            ["serif", "sans", "mono"],
        ),
    )


def activity_card(data):
    height = 340
    monthly = data["monthly"][-12:]
    max_count = max((month["total"] for month in monthly), default=0) or 1
    left, right, baseline, max_height, gap = 40, 600, 292, 140, 10
    bar_width = (right - left - gap * (len(monthly) - 1)) / max(len(monthly), 1)
    top_month = max(
        range(len(monthly)), key=lambda index: monthly[index]["total"],
        default=-1,
    )
    bars = []
    for index, month in enumerate(monthly):
        count = month["total"]
        bar_height = max(4, round(count / max_count * max_height))
        x = left + index * (bar_width + gap)
        month_date = datetime.date.fromisoformat(month["month"] + "-01")
        label = month_date.strftime("%b")
        colour = BLUE if index == top_month else INK
        start_delay = 2.2 + index * 0.07
        bars.append(
            '<rect class="g" {} x="{:.1f}" y="{}" width="{:.1f}" '
            'height="{}" rx="4" fill="{}"/>'.format(
                delay(start_delay), x, baseline - bar_height, bar_width,
                bar_height, colour,
            )
        )
        bars.append(
            text(
                "{:.1f}".format(x + bar_width / 2), baseline + 22,
                escape(label), MONO, 11, MUTED, class_name="f",
                at=start_delay, extra='text-anchor="middle"',
            )
        )
        if index == top_month:
            bars.append(
                text(
                    "{:.1f}".format(x + bar_width / 2), baseline - bar_height - 10,
                    escape("{:,}".format(count)), MONO, 11, BLUE,
                    class_name="p", at=3.2, extra='text-anchor="middle"',
                )
            )

    current = data["current_streak"]["length"]
    longest = data["longest_streak"]["length"]
    active = data["active_days"]
    total_days = len(data["days"])
    busiest = data["best_day"]
    stat_groups = [
        (
            '{} <tspan font-style="italic">days</tspan>'.format(escape(current)),
            "current streak / longest {} days".format(longest),
        ),
        (
            '{}<tspan fill="{}"> / {}</tspan>'.format(
                escape(active), MUTED, escape(total_days)
            ),
            "days with a contribution",
        ),
        (
            escape(busiest["count"]),
            "on the busiest day / {}".format(escape(busiest["date"])),
        ),
    ]
    side = []
    for index, (large, small) in enumerate(stat_groups):
        y = 104 + index * 92
        side.append(
            '<g class="r" {}>{}{}{}</g>'.format(
                delay(2.6 + index * 0.15),
                text(650, y, large, SERIF, 40, INK, class_name=""),
                text(650, y + 24, escape(small), SANS, 13, MUTED, class_name=""),
                "",
            )
        )

    content = """
<rect width="{width}" height="{height}" rx="14" fill="{paper}"/>
{heading}
{total}
{bars}
{stats}
""".format(
        width=W,
        height=height,
        paper=PAPER,
        heading=text(
            40, 58, escape("THE LAST 12 MONTHS ON GITHUB"), MONO, 12, MUTED,
            class_name="f", at=1.9, extra='letter-spacing="1"',
        ),
        total=text(
            38, 114,
            '{} <tspan font-style="italic">contributions</tspan>'.format(
                escape("{:,}".format(data["total_contributions"]))
            ),
            SERIF, 52, INK, at=2.0,
        ),
        bars="".join(bars),
        stats="".join(side),
    )
    write_card(
        "activity.svg",
        svg(
            W, height, content,
            "{:,} contributions in the last year, {}-day streak".format(
                data["total_contributions"], current
            ),
            ["serif", "serif-i", "sans", "mono"],
        ),
    )


def repo_card(slug, name, description, language, colour, start_delay):
    width = W / 3
    height = 170
    description_lines = "".join(
        text(
            24, 72 + index * 21, escape(line), SANS, 14, INK_SOFT,
            class_name="",
        )
        for index, line in enumerate(wrap(description, 34))
    )
    body = """
<rect width="{width:.1f}" height="{height}" rx="14" fill="{paper_deep}"/>
<g class="r" {group_delay}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{colour}"/>
  {name_text}
  {description_lines}
  {language_text}
</g>
""".format(
        width=width,
        height=height,
        paper_deep=PAPER_DEEP,
        group_delay=delay(start_delay),
        colour=colour,
        name_text=text(
            40, 39, escape(name), SANS, 17, INK, class_name="",
            extra='font-weight="600"',
        ),
        description_lines=description_lines,
        language_text=text(
            24, height - 24, escape(language), MONO, 12, MUTED,
            class_name="",
        ),
    )
    write_card(
        "repo-{}.svg".format(slug),
        svg(
            round(width, 2), height, body,
            "{}: {} ({})".format(name, description, language),
            ["sans", "sans-b", "mono"],
        ),
    )


def title_card(theme):
    dark = theme == "dark"
    background = "#1a1a1a" if dark else PAPER
    foreground = "#f6f1e7" if dark else INK
    body = (
        '<rect width="{}" height="64" rx="14" fill="{}"/>'
        '<text class="r" {} x="2" y="46" font-family="{}" font-size="34" '
        'fill="{}">What I am <tspan font-style="italic">coding</tspan></text>'
    ).format(
        W, background, delay(4.4), SERIF, foreground,
    )
    write_card(
        "title-coding-{}.svg".format(theme),
        svg(
            W, 64, body, "What I am coding",
            ["serif", "serif-i"], background=background,
        ),
    )


BLUE_LEVELS = [PAPER_DEEP, "#c8d3ff", "#94a8ff", "#6280ff", BLUE, "#1a3be0"]


def level(count):
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def heatmap_card(data):
    days = data["days"][-365:]
    if not days:
        raise ValueError("contribution data must include at least one day")
    first_date = datetime.date.fromisoformat(days[0]["date"])
    leading_days = (first_date.weekday() + 1) % 7
    cell, step, grid_x, grid_y = 12, 15, 44, 96
    cells = []
    months = []
    seen_months = set()
    for index, day in enumerate(days):
        column, row = divmod(index + leading_days, 7)
        day_date = datetime.date.fromisoformat(day["date"])
        if day_date.day <= 7 and (day_date.year, day_date.month) not in seen_months and row == 0:
            seen_months.add((day_date.year, day_date.month))
            months.append((column, day_date.strftime("%b")))
        count = day["count"]
        cells.append(
            '<rect class="p" {} x="{}" y="{}" width="{}" height="{}" '
            'rx="3" fill="{}"><title>{}: {} contributions</title></rect>'.format(
                delay(0.8 + column * 0.03 + row * 0.02),
                grid_x + column * step,
                grid_y + row * step,
                cell,
                cell,
                BLUE_LEVELS[level(count)],
                escape(day["date"]),
                escape(count),
            )
        )

    columns = (len(days) + leading_days + 6) // 7
    right = grid_x + columns * step - 3
    month_labels = "".join(
        text(
            grid_x + column * step, grid_y + 7 * step + 16,
            escape(month), MONO, 11, MUTED, class_name="",
        )
        for column, month in months
        if column < columns - 12
    )
    legend_x = right - len(BLUE_LEVELS) * 14
    legend = "".join(
        '<rect x="{}" y="{}" width="11" height="11" rx="2.5" fill="{}"/>'.format(
            legend_x + index * 14, grid_y + 7 * step + 6, colour
        )
        for index, colour in enumerate(BLUE_LEVELS)
    )
    height = grid_y + 7 * step + 44
    body = """
<rect width="{width}" height="{height}" rx="14" fill="{paper}"/>
{heading}
{refresh}
{cells}
<g class="f" {legend_delay}>
  {months}
  {less}
  {legend}
  {more}
</g>
""".format(
        width=W,
        height=height,
        paper=PAPER,
        heading=text(
            42, 62,
            'Every day, <tspan font-style="italic" fill="{}">in blue</tspan>'.format(BLUE),
            SERIF, 34, INK, at=0.55,
        ),
        refresh=text(
            right, 60, escape("REFRESHED DAILY"), MONO, 12, MUTED,
            class_name="f", extra='text-anchor="end" letter-spacing="1"',
        ),
        cells="".join(cells),
        legend_delay=delay(2.4),
        months=month_labels,
        less=text(
            legend_x - 8, grid_y + 7 * step + 16, escape("less"),
            MONO, 11, MUTED, class_name="", extra='text-anchor="end"',
        ),
        legend=legend,
        more=text(
            legend_x + len(BLUE_LEVELS) * 14 + 2,
            grid_y + 7 * step + 16, escape("more"),
            MONO, 11, MUTED, class_name="",
        ),
    )
    write_card(
        "heatmap.svg",
        svg(
            W, height, body,
            "Contribution graph: {:,} contributions in the last year".format(
                data["total_contributions"]
            ),
            ["serif", "mono"],
        ),
    )


def render(data):
    hero_card()
    heatmap_card(data)
    activity_card(data)
    for tile in TILES:
        tile_card(*tile)
    title_card("light")
    title_card("dark")
    for index, repository in enumerate(REPOS):
        repo_card(*repository, 4.6 + index * 0.12)


if __name__ == "__main__":
    with open(DATA_PATH, encoding="utf-8") as source:
        contribution_data = json.load(source)
    render(contribution_data)
