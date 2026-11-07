#!/usr/bin/env python3
"""Crop the hand-supplied Resend and Cloudflare screen-shots and draw the guide's red marks on them.

The marks are the same boxes and badges that capture_setup_screens.py draws on the
WordPress shots, rendered at 2x. Every crop and mark is in source-image pixels and
was measured on the shots supplied on 2026-10-25 to 2026-11-06, which come in several
window sizes; a replaced screen-shot needs new numbers, so a source of any other size
stops the tool.

Every crop leaves out the account switcher (the Resend team name, the Cloudflare login)
and the records tables' Status column. Only the -redacted copies of the API key list
shots are read (see tools/redact_image.py): their Token column showed each key's start.

Usage:
    .venv/bin/python tools/mark_resend_shots.py
"""

import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from capture_setup_screens import MARK_JS

WAT = Path(__file__).resolve().parent.parent
SRC = WAT / "materials" / "setup-guides" / "affiliate-theme" / "screenshots"
OUT = WAT / ".tmp" / "setup-guide" / "screens"

# name: (source file under SRC, its size, crop x,y,w,h, marks [(x,y,w,h, label[, pad])])
SHOTS = {
    # Step 5: the API key.
    "rs-1-api-keys": ("resend/screenshot-2-home-page-click-sidebar-to-navigate-to-api-keys-resend.png", (1366, 570),
                      (0, 64, 640, 410), [(16, 358, 217, 32, "1")]),
    "rs-2-create-key": ("resend/screenshot-3-api-keys-create-resend-redacted.png", (1366, 573),
                        (262, 22, 1094, 260), [(1160, 34, 141, 30, "2")]),
    "rs-3-add-key": ("resend/screenshot-4-api-key-add-resend.png", (1319, 582),
                     (390, 84, 540, 416), [(429, 197, 462, 32, "3"), (429, 281, 462, 32, "4"),
                                           (430, 430, 99, 30, "5")]),
    "rs-4-copy-key": ("resend/screenshot-5-api-key-view-copy-resend.png", (1319, 582),
                      (390, 141, 540, 300), [(861, 321, 24, 22, "6", 3), (430, 373, 59, 30, "7")]),
    # Step 7: the domain and its records.
    "rs-5-domains": ("resend/screenshot-8-domains-resend.png", (1366, 575),
                     (262, 22, 1094, 250), [(358, 193, 258, 28, "1", 3)]),
    "rs-6-domain": ("resend/screenshot-9-domain-status-not-started-resend.png", (1366, 575),
                    (262, 22, 1094, 380), [(274, 358, 80, 32, "2")]),
    "rs-7-dkim": ("resend/screenshot-20-domain-dns-records-verified-resend.png", (1366, 575),
                  (286, 76, 864, 156), []),
    "rs-8-spf-tracking": ("resend/screenshot-27-domain-dns-records-four-resend.png", (1366, 581),
                          (286, 10, 898, 512), []),
    "rs-9-verified": ("resend/screenshot-19-domain-verified-ready-to-send-emails-resend.png", (1366, 575),
                      (262, 22, 1094, 320), [(489, 177, 63, 23, "", 3)]),
    "cf-1-domain": ("cloudflare/screenshot-11-account-home-cloudflare.png", (1319, 582),
                    (276, 314, 344, 90), [(292, 366, 320, 24, "1", 3)]),
    "cf-2-records": ("cloudflare/screenshot-13-dns-records-cloudflare.png", (1366, 575),
                     (0, 62, 1366, 450), [(42, 421, 203, 30, "2", 3), (485, 469, 119, 37, "3", 3)]),
    "cf-3-txt": ("cloudflare/screenshot-15-save-txt-record-cloudflare.png", (1366, 575),
                 (299, 64, 769, 511), [(442, 284, 594, 37, "4", 3), (330, 355, 594, 102, "5", 3),
                                       (330, 533, 98, 37, "6", 3)]),
    "cf-4-cname": ("cloudflare/screenshot-18-save-record-cname-cloudflare.png", (1366, 575),
                   (299, 64, 769, 434), [(782, 310, 136, 24, "7", 3)]),
    # Step 7's box: a domain that was already in Resend.
    "rs-10-configure": ("resend/screenshot-21-configuration-enable-tracking-metrics-button-configure-resend.png",
                        (1325, 655), (262, 30, 1050, 360), [(362, 44, 117, 30, "1"), (299, 338, 92, 32, "2")]),
    "rs-11-tracking": ("resend/screenshot-22-enable-open-tracking-resend.png", (1326, 541),
                       (330, 30, 470, 385), [(364, 258, 170, 19, "3", 2), (364, 290, 172, 19, "4", 2),
                                             (364, 163, 132, 32, "5")]),
    "rs-12-auto-configure": ("resend/screenshot-25-auto-configure-resend.png", (1319, 582),
                             (340, 140, 790, 310), [(364, 397, 151, 31, "6"), (530, 401, 160, 22, "", 3)]),
    "rs-13-partially": ("resend/screenshot-26-domain-restart-verification-resend.png", (1319, 582),
                        (262, 22, 1050, 190), [(480, 177, 112, 23, "", 3)]),
    # Step 7's optional section: receiving replies. The toggle sits right of the
    # Status column, so rs-14 shows the heading row only and rs-15 the MX row
    # without its Status.
    "rs-14-receiving": ("resend/screenshot-28-rs-tick-enable-receiving.png", (1326, 541),
                        (286, 88, 1010, 62), [(1235, 109, 44, 28, "1", 3)]),
    "rs-15-receiving-mx": ("resend/screenshot-30-rs-enable-receiving-verified.png", (1326, 541),
                           (286, 145, 858, 125), [(300, 226, 540, 26, "2", 3)]),
    "cf-5-mx": ("cloudflare/screenshot-29-cf-receiving-records.png", (1326, 541),
                (296, 195, 736, 272), [(310, 231, 706, 38, "", 3), (310, 302, 594, 38, "", 3),
                                       (310, 417, 98, 38, "", 3)]),
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1366, "height": 600}, device_scale_factor=2)
        for name, (src, want, (x, y, w, h), marks) in SHOTS.items():
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
