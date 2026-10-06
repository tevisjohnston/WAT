#!/usr/bin/env python3
"""Render SETUP-GUIDE.pdf from tools/templates/setup_guide.{html,css}.

Inputs:
  - .tmp/setup-guide/screens/[0-9]*.png   from tools/capture_setup_screens.py
  - .tmp/setup-guide/screens/gr-*.png     from tools/mark_getresponse_shots.py, which
    crops and marks the GetResponse screen-shots supplied by hand
  - the wp-dfy theme's fonts and style.css Version

Every <img> must exist. The GetResponse screen-shots may be missing only with
--draft, which swaps in a dashed placeholder and stamps DRAFT on every page, so
a buyer-facing PDF never ships with a hole in it.

Usage:
    .venv/bin/python tools/build_setup_guide.py [--draft] [--out deliverables/SETUP-GUIDE.pdf]
"""

import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

WAT = Path(__file__).resolve().parent.parent
THEME = Path("/home/tevis/wp-dfy/wp-content/themes/affiliate-theme")
TEMPLATES = WAT / "tools" / "templates"
SCREENS = WAT / ".tmp" / "setup-guide" / "screens"
RENDERED = WAT / ".tmp" / "setup-guide" / "guide.html"


def theme_version() -> str:
    match = re.search(r"^Version:\s*(\S+)", (THEME / "style.css").read_text(), re.M)
    if not match:
        raise RuntimeError("no Version header in the theme's style.css")
    return match.group(1)


def render_html(draft: bool) -> tuple[str, list[str]]:
    css = (TEMPLATES / "setup_guide.css").read_text()
    html = (TEMPLATES / "setup_guide.html").read_text()
    html = html.replace("{{CSS}}", css)
    html = html.replace("{{FONTS}}", (THEME / "assets" / "fonts").as_uri())
    html = html.replace("{{SCREENS}}", SCREENS.as_uri())
    html = html.replace("{{VERSION}}", theme_version())
    html = html.replace("{{DRAFT}}", '<div class="draft-mark">DRAFT</div>' if draft else "")

    leftover = sorted(set(re.findall(r"\{\{[A-Z]+\}\}", html)))
    if leftover:
        raise RuntimeError(f"unfilled template tokens: {leftover}")

    problems = []

    def check(match: re.Match) -> str:
        tag = match.group(0)
        src = re.search(r'src="file://([^"]+)"', tag).group(1)
        if Path(src).is_file():
            return tag
        if draft and "data-gr" in tag:
            return f'<div class="missing">GetResponse screen-shot pending: {Path(src).name}</div>'
        problems.append(src)
        return tag

    html = re.sub(r"<img\b[^>]*>", check, html)
    return html, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--draft", action="store_true", help="allow missing GetResponse screen-shots")
    parser.add_argument("--out", default=str(WAT / "deliverables" / "SETUP-GUIDE.pdf"))
    args = parser.parse_args()
    out = Path(args.out)

    html, missing = render_html(args.draft)
    if missing:
        print("ERROR: missing images (run capture_setup_screens.py and mark_getresponse_shots.py):",
              *missing, sep="\n  ", file=sys.stderr)
        return 1

    RENDERED.parent.mkdir(parents=True, exist_ok=True)
    RENDERED.write_text(html)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(RENDERED.as_uri(), wait_until="load")
        page.evaluate("() => document.fonts.ready")
        broken = page.evaluate("() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src)")
        if broken:
            print("ERROR: images failed to load:", *broken, sep="\n  ", file=sys.stderr)
            return 1
        page.pdf(path=str(out), format="Letter", print_background=True, prefer_css_page_size=True,
                 tagged=True, outline=True)
        browser.close()

    print(f"wrote {out}{' (DRAFT)' if args.draft else ''}  {out.stat().st_size / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
