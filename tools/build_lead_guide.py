#!/usr/bin/env python3
"""Render the landing-3 guide.pdf from tools/templates/lead_guide.{html,css}.

The Long Form landing page of the wp-dfy affiliate theme promises "the guide",
and its first email delivers it: the theme puts guide.pdf next to index.html in
that email's ZIP. This tool prints the guide and copies it into the theme at
emails/landing-3/guide.pdf, which is then committed in wp-dfy like any theme file.

Inputs:
  - tools/templates/lead_guide.html + lead_guide.css   the guide copy and layout
  - the wp-dfy theme's fonts                           assets/fonts/
  - the theme's landing-3 pattern                      its "What Is In The Guide" list

Every bullet of that list must appear in the guide word for word (its chapter
titles), so a change to the landing page's promise can't pass unnoticed.

Usage:
    .venv/bin/python tools/build_lead_guide.py [--no-copy]
"""

import argparse
import html as htmllib
import re
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

WAT = Path(__file__).resolve().parent.parent
THEME = Path("/home/tevis/wp-dfy/wp-content/themes/affiliate-theme")
TEMPLATES = WAT / "tools" / "templates"
OUT_DIR = WAT / ".tmp" / "lead-guide"
RENDERED = OUT_DIR / "guide.html"
PDF = OUT_DIR / "guide.pdf"
THEME_PDF = THEME / "emails" / "landing-3" / "guide.pdf"
# The whole ZIP may be 10 MB in GetResponse; keep the guide far below that.
MAX_BYTES = 2 * 1024 * 1024


def landing_promises() -> list[str]:
    """The <li> texts under "What Is In The Guide" in the Long Form pattern function."""
    src = (THEME / "inc" / "affiliate-theme-funnel.php").read_text()
    body = re.search(r"function Affiliate_Theme_Theme_landing_pattern_long\b(.*?)\nfunction ", src, re.S)
    if not body:
        raise RuntimeError("Affiliate_Theme_Theme_landing_pattern_long() not found")
    section = body.group(1).split("What Is In The Guide", 1)
    if len(section) != 2:
        raise RuntimeError('"What Is In The Guide" not found in the Long Form pattern')
    items = re.findall(r"<li>(.*?)</li>", section[1].split("</ul>", 1)[0], re.S)
    if not items:
        raise RuntimeError("no list items under \"What Is In The Guide\"")
    return [htmllib.unescape(i).strip().rstrip(".") for i in items]


def render_html() -> str:
    css = (TEMPLATES / "lead_guide.css").read_text()
    html = (TEMPLATES / "lead_guide.html").read_text()
    html = html.replace("{{CSS}}", css)
    html = html.replace("{{FONTS}}", (THEME / "assets" / "fonts").as_uri())

    leftover = sorted(set(re.findall(r"\{\{[A-Z]+\}\}", html)))
    if leftover:
        raise RuntimeError(f"unfilled template tokens: {leftover}")
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-copy", action="store_true", help="build into .tmp only; don't touch the theme")
    args = parser.parse_args()

    html = render_html()
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"\s+", " ", text)
    missing = [p for p in landing_promises() if p not in text]
    if missing:
        print("ERROR: the guide no longer covers what the landing page promises:", *missing,
              sep="\n  ", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RENDERED.write_text(html)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(RENDERED.as_uri(), wait_until="load")
        page.evaluate("() => document.fonts.ready")
        loaded = page.evaluate("() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
        loaded = {name.strip('"') for name in loaded}
        if not {"Archivo", "Newsreader"} <= loaded:
            print(f"ERROR: the theme fonts did not load (loaded: {sorted(loaded)})", file=sys.stderr)
            return 1
        page.pdf(path=str(PDF), format="Letter", print_background=True, prefer_css_page_size=True,
                 tagged=True, outline=True)
        browser.close()

    size = PDF.stat().st_size
    if size > MAX_BYTES:
        print(f"ERROR: {PDF} is {size / 1024 / 1024:.2f} MB, over the {MAX_BYTES // 1024 // 1024} MB cap",
              file=sys.stderr)
        return 1

    print(f"wrote {PDF}  {size / 1024:.0f} KB")
    if not args.no_copy:
        shutil.copyfile(PDF, THEME_PDF)
        print(f"copied to {THEME_PDF}  (commit it in /home/tevis/wp-dfy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
