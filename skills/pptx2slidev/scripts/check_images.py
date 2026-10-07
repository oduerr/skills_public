"""Check that the deck uses pictures the way PowerPoint showed them.

Usage: python check_images.py DECK.md WORK [--public-dir public]

WORK is the extract.py folder (pictures.json, media/). Every image the deck uses
(also in `src:` imports) is matched by content (small thumbnail + aspect ratio,
so renamed or re-encoded files are found too) against the extracted pictures:

  ERROR uncropped   the deck shows the RAW picture although PowerPoint cropped it.
                    Crops often hide private content (browser tabs), quiz answers or
                    extra data. Use the cropped file from media/.
  WARN  rotated     PowerPoint rotated the picture; check the slide (CSS rotate-*).
  WARN  stretched   PowerPoint showed it stretched; check the slide.
  INFO  no match    image not found in the .pptx (crop of the reference page, new image)

Exit code 1 if there is an ERROR.
Needs: Pillow.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck import read_deck  # noqa: E402

IMG = [r'<img[^>]+src="([^"]+)"', r"!\[[^\]]*\]\(([^)\s]+)", r"^(?:image|background):\s*['\"]?([^'\"\s]+)"]


def sig(path):
    im = Image.open(path)
    im.load()
    w, h = im.size
    g = im.convert("L").resize((24, 24))
    data = g.get_flattened_data() if hasattr(g, "get_flattened_data") else g.getdata()
    return w / h if h else 1.0, list(data)


def dist(a, b):
    ra, pa = a
    rb, pb = b
    pix = sum(abs(x - y) for x, y in zip(pa, pb)) / (len(pa) * 255)
    return pix + 2 * abs(ra / rb - 1)


def project_public(deck, arg):
    if arg:
        return (deck.parent / arg).resolve()
    for d in [deck.parent, *deck.parents]:
        if (d / "public").is_dir():
            return d / "public"
    return deck.parent / "public"


def main():
    deck, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    pub = project_public(deck, sys.argv[sys.argv.index("--public-dir") + 1] if "--public-dir" in sys.argv else None)
    pics = json.load(open(work / "pictures.json"))
    cands = []
    for p in pics:
        f = work / "media" / p["file"]
        if f.exists():
            try:
                cands.append(("crop" if p["raw"] else "pic", p, sig(f)))
            except Exception:
                pass
        if p["raw"] and (work / "media" / p["raw"]).exists():
            try:
                cands.append(("raw", p, sig(work / "media" / p["raw"])))
            except Exception:
                pass

    refs = {}
    for k, s in enumerate(read_deck(deck), 1):
        for pat in IMG:
            for m in re.finditer(pat, s["body"] + "\n" + "\n".join(f"{a}: {b}" for a, b in s["fm"].items()), re.M):
                src = m.group(1)
                if not src.startswith(("http://", "https://", "data:")):
                    line = s["body"][max(0, m.start() - 0): m.end() + 200]
                    refs.setdefault(src, []).append((k, line))

    errors = 0
    for src, uses in sorted(refs.items()):
        f = pub / src.lstrip("/")
        if not f.exists():
            print(f"WARN  missing   {src} (slides {sorted({k for k, _ in uses})})")
            continue
        try:
            sg = sig(f)
        except Exception:
            continue
        scored = sorted(((dist(sg, c[2]), c) for c in cands), key=lambda x: x[0])
        if not scored or scored[0][0] > 0.25:
            print(f"INFO  no match  {src}")
            continue
        d, (kind, p, _) = scored[0]
        slides = sorted({k for k, _ in uses})
        if kind == "raw":
            # only an error if the cropped version is clearly different
            crop_d = next((x for x, c in scored if c[0] == "crop" and c[1] is p), 9)
            # the same picture may be used uncropped on another slide: then it is fine
            uncropped_elsewhere = any(c[0] == "pic" and x - d < 0.02 for x, c in scored)
            if crop_d - d > 0.02 and not uncropped_elsewhere:
                errors += 1
                print(f"ERROR uncropped {src} (deck slides {slides}) = RAW of pptx slide {p['slide']} picture; "
                      f"PowerPoint crops L/T/R/B={'/'.join(f'{c:.0f}' for c in p['crop'])}%. Use media/{p['file']}.")
                continue
        if p.get("rot"):
            if not any(re.search(r"rotate", line) for _, line in uses):
                print(f"WARN  rotated   {src} (deck slides {slides}): PowerPoint rotates it by {p['rot']:.0f} deg; no rotate class found")
        if p.get("stretch"):
            print(f"WARN  stretched {src} (deck slides {slides}): PowerPoint frame/image ratio {p['stretch']}; check the slide")
    print(f"{len(refs)} images checked, {errors} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
