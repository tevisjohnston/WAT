#!/usr/bin/env python3
"""Crop the hand-supplied GetResponse screenshots and draw the guide's red marks on them.

The marks are the same boxes and badges that capture_setup_screens.py draws on the
WordPress shots, rendered at 2x. Every crop and mark is in source-image pixels and
was measured on the shots supplied on 2026-09-28 (1366x563, except the list menu
shot at 1366x606); a replaced screenshot needs new numbers, so any other size stops
the tool.

Only the -REDACTED copy of the API key shot is read (see tools/redact_image.py).

Usage:
    .venv/bin/python tools/mark_getresponse_shots.py
"""

import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from capture_setup_screens import MARK_JS

WAT = Path(__file__).resolve().parent.parent
SRC = WAT / "setup-guide-edits" / "setup-guide-screenshots-getresponse"
OUT = WAT / ".tmp" / "setup-guide" / "screens"
SIZE = (1366, 563)
SIZES = {"gr-8-list-menu": (1366, 606)}

# name: (source file, crop x,y,w,h, marks [(x,y,w,h, label[, pad])])
SHOTS = {
    "gr-1-tools": ("Screenshot-Dashboard-Marketing-Software-GetResponse.png",
                   (0, 0, 680, 180), [(94, 14, 88, 34, "1")]),
    "gr-2-integrations": ("Screenshot-Tools-Marketing-Software-GetResponse.png",
                          (500, 70, 680, 200), [(797, 119, 135, 22, "2")]),
    "gr-3-api-tab": ("Screenshot-Integrations-API-Marketing-Software-GetResponse.png",
                     (40, 105, 620, 190), [(478, 136, 44, 28, "3")]),
    "gr-4-generate": ("Screenshot-API-Marketing-Software-GetResponse.png",
                      (660, 210, 600, 340), [(693, 478, 191, 44, "4")]),
    "gr-5-name-key": ("Screenshot-generate-API-key-Marketing-Software-GetResponse.png",
                      (323, 120, 720, 323), [(433, 270, 500, 44, ""), (801, 341, 132, 44, "5")]),
    "gr-6-copy-key": ("Screenshot-API-key-Email-Marketing-Software-GetResponse-REDACTED.png",
                      (323, 70, 720, 300), [(853, 296, 80, 44, "6")]),
    "gr-7-lists": ("Screenshot-lists-Marketing-Software-GetResponse.png",
                   (0, 0, 650, 430), [(212, 14, 86, 34, "1")]),
    "gr-8-list-menu": ("Screenshot-lists-3-dots-settings-Marketing-Software-GetResponse.png",
                       (1010, 108, 340, 330), [(1280, 380, 24, 28, ""), (1068, 181, 80, 34, "2")]),
    "gr-9-list-token": ("Screenshot-2-list-token-Marketing-Software-GetResponse.png",
                        (413, 250, 540, 135), [(430, 354, 93, 15, "", 2)]),
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]}, device_scale_factor=2)
        for name, (src, (x, y, w, h), marks) in SHOTS.items():
            want = SIZES.get(name, SIZE)
            page.set_viewport_size({"width": want[0], "height": want[1]})
            data = base64.b64encode((SRC / src).read_bytes()).decode()
            page.set_content(f'<body style="margin:0"><img src="data:image/png;base64,{data}" style="display:block"></body>')
            page.wait_for_function("() => document.images[0].complete && document.images[0].naturalWidth > 0")
            size = tuple(page.evaluate("() => [document.images[0].naturalWidth, document.images[0].naturalHeight]"))
            if size != want:
                print(f"ERROR: {src} is {size[0]}x{size[1]}, not {want[0]}x{want[1]}; re-measure its crop and marks",
                      file=sys.stderr)
                return 1
            for mx, my, mw, mh, label, *pad in marks:
                page.evaluate(MARK_JS, [{"x": mx, "y": my, "width": mw, "height": mh}, label, pad[0] if pad else 5, "left"])
            path = OUT / f"{name}.png"
            page.screenshot(path=str(path), clip={"x": x, "y": y, "width": w, "height": h})
            print(f"  {path.relative_to(WAT)}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
