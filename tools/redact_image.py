#!/usr/bin/env python3
"""Paint solid boxes over parts of a screenshot and write a new PNG.

Each box is x,y,w,h in image pixels, optionally followed by :TEXT to print in it.
The fill colour is sampled from the pixel just left of the box, so the patch
matches the surrounding background (or pass --fill #rrggbb).

Usage:
    .venv/bin/python tools/redact_image.py IN.png OUT.png --box 436,299,415,39:•••••••• --box 60,370,110,20
"""

import argparse
import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAINT_JS = """
async ([src, boxes, fill]) => {
  const img = new Image();
  img.src = src;
  await img.decode();
  const c = document.createElement('canvas');
  c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d');
  g.drawImage(img, 0, 0);
  for (const b of boxes) {
    let color = fill;
    if (!color) {
      const [r, gr, bl] = g.getImageData(Math.max(0, b.x - 2), b.y + 2, 1, 1).data;
      color = `rgb(${r},${gr},${bl})`;
    }
    g.fillStyle = color;
    g.fillRect(b.x, b.y, b.w, b.h);
    if (b.text) {
      g.fillStyle = '#4b5563';
      g.font = `${Math.round(b.h * 0.42)}px Arial, sans-serif`;
      g.textBaseline = 'middle';
      g.fillText(b.text, b.x + 10, b.y + b.h / 2);
    }
  }
  return c.toDataURL('image/png');
}
"""


def parse_box(spec: str) -> dict:
    coords, _, text = spec.partition(":")
    x, y, w, h = (int(v) for v in coords.split(","))
    return {"x": x, "y": y, "w": w, "h": h, "text": text}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src")
    parser.add_argument("out")
    parser.add_argument("--box", action="append", required=True, type=parse_box)
    parser.add_argument("--fill", default="", help="fill colour; default samples the background")
    args = parser.parse_args()

    src, out = Path(args.src).resolve(), Path(args.out).resolve()
    if src == out:
        print("ERROR: write to a new file; the original is kept", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        page = browser.new_page()
        page.goto(src.parent.as_uri() + "/")
        data_url = page.evaluate(PAINT_JS, [src.as_uri(), args.box, args.fill])
        browser.close()

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(data_url.split(",", 1)[1]))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
