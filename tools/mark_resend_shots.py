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
SRC = WAT / "materials" / "guides" / "affiliate-theme" / "screenshots"
OUT = WAT / ".tmp" / "affiliate-theme-guide" / "screens"

# name: (source file under SRC, its size, crop x,y,w,h, marks [(x,y,w,h, label[, pad])])
SHOTS = {
    # Step 1: the members page's Downloadable Resources card, with the theme's zip row marked.
    "amc-1-download": ("affiliate-market-connect/screenshot-1-amc.png", (1308, 2125),
                       (350, 1334, 928, 555), [(383, 1660, 862, 90, "1", 3)]),
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
    "cf-1-2-domain-dns-records": ("cloudflare/cf-1-2-domain-dns-records.png", (402, 173),
                                  (0, 0, 402, 173), [(29, 131, 90, 24, "2", 3)]),
    "cf-2-records": ("cloudflare/screenshot-13-dns-records-cloudflare.png", (1366, 575),
                     (0, 62, 1366, 450), [(485, 469, 119, 37, "3", 3)]),
    "cf-4-cname": ("cloudflare/screenshot-18-save-record-cname-cloudflare.png", (1366, 575),
                   (299, 64, 769, 434), [(330, 231, 99, 38, "4", 3), (443, 231, 593, 38, "5", 3),
                                         (330, 302, 438, 38, "6", 3), (782, 302, 234, 38, "7", 3),
                                         (330, 421, 98, 38, "8", 3)]),
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

# The shots were taken on the owner's test domain, wp-guide.affiliatemarketconnect.com (a
# subdomain, so Resend names its records send.wp-guide and so on). PAINT makes them show the
# apex yoursite.com that the WordPress shots and the guide use, before the marks are drawn:
# - erase: paint a box with the background (the commonest colour just above it), which drops
#   a record name's ".wp-guide" ending, leaving "send" as a buyer on their main domain sees it.
# - text: replace a word. Its box is the old word's ink (found with tesseract, in source pixels);
#   the new text is sized so the old word would fill that box, in Inter (Resend's and
#   Cloudflare's type) or a monospace font, in the darkest colour found in the box. "tail" moves
#   the rest of the line, up to that x, left against the shorter word; "under" keeps that many
#   pixel rows of an underline below the word, cut to the new width.
# - move: shift a box (a check mark after a shortened name) to a new x.
# Every source here was viewed after painting; the crops show no wp-guide or affiliatemarketconnect.
HEAD = {"old": "wp-guide.affiliatemarketconnect.com", "new": "yoursite.com", "weight": 600}
PAINT = {
    "resend/screenshot-4-api-key-add-resend.png": [
        {"text": (442, 207, 178, 11), "old": "affiliatemarketconnect.com", "new": "yoursite.com"}],
    "resend/screenshot-8-domains-resend.png": [
        {"text": (362, 200, 246, 14), "old": "wp-guide.affiliatemarketconnect.com", "new": "yoursite.com",
         "under": 5}],
    "resend/screenshot-9-domain-status-not-started-resend.png": [{"text": (378, 74, 467, 26), **HEAD}],
    "resend/screenshot-19-domain-verified-ready-to-send-emails-resend.png": [{"text": (378, 74, 467, 26), **HEAD}],
    "resend/screenshot-26-domain-restart-verification-resend.png": [{"text": (378, 74, 467, 26), **HEAD}],
    "resend/screenshot-20-domain-dns-records-verified-resend.png": [
        {"erase": (541, 198, 81, 18)}, {"move": (622, 196, 16, 21), "to": 551}],
    "resend/screenshot-27-domain-dns-records-four-resend.png": [
        {"erase": (427, 136, 73, 17)}, {"erase": (427, 177, 73, 17)},
        {"erase": (435, 218, 73, 17)}, {"erase": (435, 484, 73, 17)}],
    "resend/screenshot-22-enable-open-tracking-resend.png": [
        {"text": (539, 175, 214, 14), "old": "wp-guide.affiliatemarketconnect", "new": "yoursite.com"}],
    "resend/screenshot-25-auto-configure-resend.png": [{"erase": (513, 328, 74, 17)}],
    "resend/screenshot-30-rs-enable-receiving-verified.png": [
        {"text": (391, 232, 66, 14), "old": "wp-guide", "new": "@", "mono": True}],
    "cloudflare/screenshot-11-account-home-cloudflare.png": [
        {"text": (318, 372, 178, 11), "old": "affiliatemarketconnect.com", "new": "yoursite.com"}],
    "cloudflare/screenshot-13-dns-records-cloudflare.png": [
        {"text": (515, 97, 369, 22), "old": "affiliatemarketconnect.com", "new": "yoursite.com", "weight": 600}],
    "cloudflare/screenshot-18-save-record-cname-cloudflare.png": [
        {"text": (332, 169, 331, 16), "old": "rsend.wp-guide.affiliatemarketconnect.com",
         "new": "rsend.yoursite.com", "weight": 600, "tail": 1040},
        {"erase": (493, 242, 66, 17)}],
    "cloudflare/screenshot-29-cf-receiving-records.png": [
        {"text": (435, 244, 61, 13), "old": "wp-guide", "new": "@"}],
}
INTER = WAT / "materials" / "fonts" / "inter" / "inter-latin-wght-normal.woff2"

PAINT_JS = """
async ([src, ops, inter]) => {
  const font = new FontFace('PaintInter', `url(data:font/woff2;base64,${inter})`, {weight: '100 900'});
  await font.load(); document.fonts.add(font);
  const img = new Image(); img.src = src; await img.decode();
  const c = document.createElement('canvas');
  c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d', {willReadFrequently: true});
  g.drawImage(img, 0, 0);
  const bgAbove = (x, y, w) => {            // the commonest colour in the row above a box
    const d = g.getImageData(x, Math.max(0, y - 2), w, 1).data, n = {};
    let best = '', top = 0;
    for (let i = 0; i < d.length; i += 4) {
      const k = `rgb(${d[i]},${d[i + 1]},${d[i + 2]})`; n[k] = (n[k] || 0) + 1;
      if (n[k] > top) { top = n[k]; best = k; }
    }
    return best;
  };
  const darkest = (x, y, w, h) => {
    const d = g.getImageData(x, y, w, h).data; let lum = 999, col = '#000';
    for (let i = 0; i < d.length; i += 4) {
      const l = 0.3 * d[i] + 0.59 * d[i + 1] + 0.11 * d[i + 2];
      if (l < lum) { lum = l; col = `rgb(${d[i]},${d[i + 1]},${d[i + 2]})`; }
    }
    return col;
  };
  for (const op of ops) {
    if (op.erase) {
      const [x, y, w, h] = op.erase;
      g.fillStyle = bgAbove(x, y, w); g.fillRect(x, y, w, h);
    } else if (op.move) {
      const [x, y, w, h] = op.move, part = g.getImageData(x, y, w, h);
      g.fillStyle = bgAbove(x, y, w); g.fillRect(x, y, w, h);
      g.putImageData(part, op.to, y);
    } else if (op.text) {
      const [x, y, w, h] = op.text;
      const bg = bgAbove(x, y, w), ink = darkest(x, y, w, h);
      const family = op.mono ? '"DejaVu Sans Mono", monospace' : 'PaintInter';
      const weight = op.weight || 400;
      g.font = `${weight} 100px ${family}`;
      const m = g.measureText(op.old);
      const size = 100 * h / (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent);
      g.font = `${weight} ${size}px ${family}`;
      const om = g.measureText(op.old), nm = g.measureText(op.new);
      const sx = op.mono ? 1 : w / (om.actualBoundingBoxRight + om.actualBoundingBoxLeft);
      const newW = Math.ceil((nm.actualBoundingBoxRight + nm.actualBoundingBoxLeft) * sx);
      const under = op.under ? g.getImageData(x, y + h + 1, newW, op.under) : null;
      const tail = op.tail ? g.getImageData(x + w + 3, y - 3, op.tail - (x + w + 3), h + 6) : null;
      g.fillStyle = bg; g.fillRect(x - 2, y - 3, (op.tail || x + w + 2) - (x - 2), h + 6 + (op.under || 0));
      if (under) g.putImageData(under, x, y + h + 1);
      if (tail) g.putImageData(tail, x + newW + 3, y - 3);
      g.save(); g.translate(x, y + om.actualBoundingBoxAscent); g.scale(sx, 1);
      g.fillStyle = ink; g.textBaseline = 'alphabetic';
      g.fillText(op.new, nm.actualBoundingBoxLeft, 0); g.restore();
    }
  }
  return c.toDataURL('image/png');
}
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    inter = base64.b64encode(INTER.read_bytes()).decode()
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1366, "height": 600}, device_scale_factor=2)
        for name, (src, want, (x, y, w, h), marks) in SHOTS.items():
            page.set_viewport_size({"width": want[0], "height": want[1]})
            data = base64.b64encode((SRC / src).read_bytes()).decode()
            if src in PAINT:
                page.set_content("<body></body>")
                painted = page.evaluate(PAINT_JS, [f"data:image/png;base64,{data}", PAINT[src], inter])
                data = painted.split(",", 1)[1]
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
