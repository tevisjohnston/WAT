#!/usr/bin/env python3
"""Render The Affiliate Marketing Blueprint PDF from tools/templates/blueprint.{html,css}.

The blueprint is the 7figure site's lead magnet: WelcomeEmail links it at
wp-content/uploads/lead-magnets/The-Affiliate-Marketing-Blueprint.pdf. This tool only
builds it into deliverables/; copying it to the 7figure site is a separate, manual step.

Inputs:
  - tools/templates/blueprint.html + blueprint.css         the copy and layout
  - materials/lead-magnets/The-Affiliate-Marketing-Blueprint/images/   the illustrations
  - the 7_Figure_Affiliate theme's Manrope woff2           assets/css/src/fonts/
  - materials/fonts/fraunces/                              Fraunces (the theme never loads it)
  - materials/fonts/newsreader/                            Newsreader, for Fraunces' lowercase f only

The illustrations are re-encoded to JPEG first: Chrome embeds a PNG losslessly, which is
what made the Gamma export 2.9 MB. The cover is clipboard.jpg with its drawn checklist
moved down the paper to make room for the live title.

The campaign roadmap is checked before printing: each campaign's numbers must chain into
the next and end at the goal, and every figure shown must match them.

Usage:
    .venv/bin/python tools/build_blueprint.py [--out PATH]
"""

import argparse
import re
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

WAT = Path(__file__).resolve().parent.parent
TEMPLATES = WAT / "tools" / "templates"
IMAGES = WAT / "materials" / "lead-magnets" / "The-Affiliate-Marketing-Blueprint" / "images"
FONTS = Path("/home/tevis/7figure.affiliatemarketconnect.com/wp-content/themes/7_Figure_Affiliate/assets/css/src/fonts")
FRAUNCES = WAT / "materials" / "fonts" / "fraunces"
NEWSREADER = WAT / "materials" / "fonts" / "newsreader"
OUT_DIR = WAT / ".tmp" / "blueprint"
RENDERED = OUT_DIR / "blueprint.html"
DEFAULT_OUT = WAT / "deliverables" / "The-Affiliate-Marketing-Blueprint.pdf"
# The welcome email links the PDF for download; keep it light.
MAX_BYTES = 2 * 1024 * 1024

STEP_ART = ["product-selection.png", "domain-and-web-hosting.png", "website-creation.png", "traffic-generation.png"]
JPEG_QUALITY = 85

# Pixel geometry of clipboard.jpg (896 x 1152). Re-measure if the image is replaced; the
# cover's text positions in blueprint.html/.css use the same grid.
PAPER_WHITE = (254, 254, 254)
CHECKLIST = (270, 310, 660, 760)   # the drawn checkboxes and lines, cut out and blanked
CHECKLIST_SCALE = 0.72
CHECKLIST_AT = (319, 578)          # where the scaled copy goes, near the foot of the paper


def prepare_images() -> Path:
    """Write the cover and the JPEG copies of the art into .tmp/blueprint/images/."""
    out = OUT_DIR / "images"
    out.mkdir(parents=True, exist_ok=True)
    for name in STEP_ART + ["funnel.jpg", "clipboard.jpg"]:
        if not (IMAGES / name).is_file():
            raise FileNotFoundError(IMAGES / name)

    for name in STEP_ART + ["funnel.jpg"]:
        Image.open(IMAGES / name).convert("RGB").save(out / (Path(name).stem + ".jpg"), quality=JPEG_QUALITY, optimize=True)

    board = Image.open(IMAGES / "clipboard.jpg").convert("RGB")
    checklist = board.crop(CHECKLIST)
    w, h = checklist.size
    checklist = checklist.resize((round(w * CHECKLIST_SCALE), round(h * CHECKLIST_SCALE)), Image.LANCZOS)
    board.paste(PAPER_WHITE, CHECKLIST)
    board.paste(checklist, CHECKLIST_AT)
    board.save(out / "cover.jpg", quality=90, optimize=True)
    return out


def render_html(images: Path) -> str:
    css = (TEMPLATES / "blueprint.css").read_text()
    html = (TEMPLATES / "blueprint.html").read_text()
    html = html.replace("{{CSS}}", css)
    html = html.replace("{{FONTS}}", FONTS.as_uri())
    html = html.replace("{{FRAUNCES}}", FRAUNCES.as_uri())
    html = html.replace("{{NEWSREADER}}", NEWSREADER.as_uri())
    html = html.replace("{{IMAGES}}", images.as_uri())

    leftover = sorted(set(re.findall(r"\{\{[A-Z]+\}\}", html)))
    if leftover:
        raise RuntimeError(f"unfilled template tokens: {leftover}")
    for src in re.findall(r'(?:src="|url\(")file://([^")]+)', html):
        if not Path(src).is_file():
            raise FileNotFoundError(src)
    return html


class RoadmapParser(HTMLParser):
    """Collects #roadmap's data-* and each .campaign's data-* plus its data-v cell texts."""

    def __init__(self):
        super().__init__()
        self.roadmap = None
        self.campaigns = []
        self.cell = None   # (name, text parts) while inside a data-v element

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id") == "roadmap":
            self.roadmap = {k[5:]: v for k, v in a.items() if k.startswith("data-")}
        if "campaign" in (a.get("class") or "").split():
            self.campaigns.append({"data": {k[5:]: v for k, v in a.items() if k.startswith("data-")}, "cells": []})
        if "data-v" in a:
            self.cell = (a["data-v"], [])

    def handle_data(self, data):
        if self.cell:
            self.cell[1].append(data)

    def handle_endtag(self, tag):
        if self.cell:
            self.campaigns[-1]["cells"].append((self.cell[0], "".join(self.cell[1]).strip()))
            self.cell = None


def money(n: Decimal) -> str:
    return ("−" if n < 0 else "") + f"${abs(n):,.0f}"


def check_roadmap(html: str) -> list[str]:
    """Every campaign must chain into the next and every shown figure must match."""
    p = RoadmapParser()
    p.feed(html)
    if not p.roadmap or not p.campaigns:
        return ["no #roadmap section or no .campaign blocks found"]
    errors = []
    start, traffic, goal, roi = (Decimal(p.roadmap[k]) for k in ("start", "traffic", "goal", "roi"))

    budget = traffic
    subscribers = 0
    for i, c in enumerate(p.campaigns, 1):
        d = {k: Decimal(v) for k, v in c["data"].items()}
        if d["budget"] != budget:
            errors.append(f"campaign {i}: budget {d['budget']} but the previous campaign left {budget}")
        spend = d["clicks"] * d["cpc"]
        new = d["clicks"] * d["optin"] / 100
        if new != new.to_integral_value():
            errors.append(f"campaign {i}: {d['optin']}% of {d['clicks']} clicks is not a whole number")
        prev = subscribers
        subscribers += int(new)
        revenue = d["sales"] * d["price"] * d["commission"] / 100
        left = d["budget"] - spend
        if left < 0:
            errors.append(f"campaign {i}: spends {spend} of a {d['budget']} budget")
        budget = left + revenue
        expect = {
            "budget": money(d["budget"]), "clicks": f"{d['clicks']:,.0f}", "spend": money(spend),
            "new": f"{new:,.0f}", "prev": f"{prev:,}", "list": f"{subscribers:,}", "sales": f"{d['sales']:,.0f}",
            "revenue": money(revenue), "left": money(left), "next": money(budget),
        }
        for name, shown in c["cells"]:
            if shown != expect.get(name):
                errors.append(f"campaign {i}: {name} shows {shown!r}, the numbers give {expect.get(name)!r}")
        # The list, its previous total and the unspent reserve are shown only where the copy needs them.
        missing = set(expect) - {"list", "prev", "left"} - {name for name, _ in c["cells"]}
        if missing:
            errors.append(f"campaign {i}: no data-v cell for {sorted(missing)}")

    if budget != goal:
        errors.append(f"the last campaign ends at {budget}, not the goal {goal}")
    actual_roi = ((goal - start) / start * 100).quantize(Decimal(1))
    if actual_roi != roi:
        errors.append(f"ROI is {actual_roi}%, the page says {roi}%")
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    for figure in (money(start), money(goal), f"{roi}%"):
        if figure not in text:
            errors.append(f"{figure} does not appear on the page")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output PDF (default {DEFAULT_OUT})")
    args = parser.parse_args()

    html = render_html(prepare_images())
    errors = check_roadmap(html)
    if errors:
        print("ERROR: the campaign roadmap does not add up:", *errors, sep="\n  ", file=sys.stderr)
        return 1

    RENDERED.write_text(html)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(RENDERED.as_uri(), wait_until="load")
        page.evaluate("() => document.fonts.ready")
        loaded = page.evaluate("() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
        loaded = {name.strip('"') for name in loaded}
        if not {"Manrope", "Fraunces", "Newsreader f"} <= loaded:
            print(f"ERROR: the fonts did not load (loaded: {sorted(loaded)})", file=sys.stderr)
            return 1
        page.pdf(path=str(args.out), format="Letter", print_background=True, prefer_css_page_size=True,
                 tagged=True, outline=True)
        browser.close()

    size = args.out.stat().st_size
    if size > MAX_BYTES:
        print(f"ERROR: {args.out} is {size / 1024 / 1024:.2f} MB, over the {MAX_BYTES // 1024 // 1024} MB cap",
              file=sys.stderr)
        return 1
    print(f"wrote {args.out}  {size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
