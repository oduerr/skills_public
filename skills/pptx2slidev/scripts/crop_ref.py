"""Crop a region of a reference page, in slide coordinates.

Usage: python crop_ref.py WORK PAGE X Y W H OUT.png [--keep-footer] [--pad 1]

  PAGE         reference PDF page number (see reference.json "map": slide -> page)
  X Y W H      region in % of the SLIDE (as in dump.md: x=..% y=..% w=..% h=..%)
  --pad P      extra margin in % of the slide on every side (default 1)
  --keep-footer  do not blank the page-number corner

Uses WORK/ref_hi/p-NN.png (200 dpi) and the slide box from reference.json, so the
margins of the A4 page do not matter and no agent has to measure them again.
Near-white pixels become pure white (LibreOffice renders an off-white background),
and the bottom-right page-number corner (last 8% x 7% of the slide) is painted white
instead of cropped away, so no content next to it is lost.
Needs: Pillow.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    a = sys.argv[1:]
    work, page = Path(a[0]), int(a[1])
    x, y, w, h = map(float, a[2:6])
    out = a[6]
    pad = float(a[a.index("--pad") + 1]) if "--pad" in a else 1.0
    ref = json.load(open(work / "reference.json"))
    box = ref.get("slide_box_pt")
    files = sorted((work / "ref_hi").glob("p-*.png"))
    f = next((p for p in files if int(p.stem.split("-")[1]) == page), None)
    if f is None:
        sys.exit(f"no ref_hi page {page} in {work}/ref_hi (run reference.py --render)")
    im = Image.open(f).convert("RGB")
    s = 200 / 72  # px per pt at 200 dpi
    if box:
        bx0, by0, bx1, by1 = (v * s for v in box)
    else:
        bx0, by0, bx1, by1 = 0, 0, im.width, im.height
    bw, bh = bx1 - bx0, by1 - by0
    if "--keep-footer" not in a:
        d = ImageDraw.Draw(im)
        d.rectangle([bx1 - 0.08 * bw, by1 - 0.07 * bh, bx1, by1], fill="white")
    x0 = bx0 + (x - pad) / 100 * bw
    y0 = by0 + (y - pad) / 100 * bh
    x1 = bx0 + (x + w + pad) / 100 * bw
    y1 = by0 + (y + h + pad) / 100 * bh
    c = im.crop((max(0, round(x0)), max(0, round(y0)), min(im.width, round(x1)), min(im.height, round(y1))))
    c = c.point(lambda v: 255 if v > 243 else v)
    c.save(out)
    print(f"{out}: {c.width}x{c.height}px from page {page}")


if __name__ == "__main__":
    main()
