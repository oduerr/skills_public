"""Compare a Slidev deck with the reference PDF: one round of the check loop.

Usage: python compare.py DECK.md WORK ROUND_DIR [--no-export] [--max-pages N]

  DECK.md    the Slidev deck
  WORK       the work folder of extract.py / reference.py (needs reference.json, ref/)
  ROUND_DIR  output folder for this round, e.g. WORK/round-02

Steps
  1. Export the deck to ROUND_DIR/slidev.pdf with `slidev export` (its own private
     server; never the user's running one). --no-export reuses an existing slidev.pdf.
  2. Match Slidev pages to reference pages by text (order-preserving).
  3. Per matched pair: words of the reference page missing in the Slidev page.
     Also deck-wide missing words (robust if a slide was split or merged).
  4. Side-by-side images ROUND_DIR/cmp-NN.png (LEFT reference, RIGHT Slidev) and
     contact sheets ROUND_DIR/sheet-NN.png (6 pairs per sheet).
  5. ROUND_DIR/report.md and ROUND_DIR/report.json.

Words that are inside an image on the Slidev side (crops) show up as missing.
That is expected: the reviewer checks them on the compare image.
Needs: poppler, Pillow, Slidev with playwright-chromium (see find_slidev()).
"""
import collections
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import align, page_count, page_text  # noqa: E402
from deck import exported  # noqa: E402

WORD = re.compile(r"[A-Za-zÄÖÜäöüßÀ-ÿ]{3,}")


def find_slidev(deck_dir):
    """Slidev binary: $SLIDEV_BIN, then the deck's node_modules, then a shared runtime, then npx."""
    cands = [os.environ.get("SLIDEV_BIN"),
             str(Path(deck_dir) / "node_modules/.bin/slidev"),
             str(Path(deck_dir).parent / "node_modules/.bin/slidev"),
             os.path.expanduser("~/.local/share/slidev-runtime/node_modules/.bin/slidev")]
    for c in cands:
        if c and os.path.exists(c):
            return [c]
    return ["npx", "--yes", "@slidev/cli"]


def words(text):
    return collections.Counter(w.lower() for w in WORD.findall(text))


def main():
    deck, work, rd = sys.argv[1], sys.argv[2], sys.argv[3]
    no_export = "--no-export" in sys.argv
    deck = os.path.abspath(deck)
    os.makedirs(rd, exist_ok=True)
    pdf = os.path.join(rd, "slidev.pdf")
    if not no_export:
        cmd = find_slidev(os.path.dirname(deck)) + ["export", deck, "--output", os.path.abspath(pdf), "--timeout", "120000"]
        r = subprocess.run(cmd, cwd=os.path.dirname(deck), capture_output=True, text=True, timeout=1200)
        if r.returncode != 0 or not os.path.exists(pdf):
            print("EXPORT FAILED\n" + r.stdout[-2000:] + r.stderr[-2000:])
            sys.exit(2)

    ref = json.load(open(os.path.join(work, "reference.json")))
    rpdf = ref["pdf"]
    rn, sn = page_count(rpdf), page_count(pdf)
    rtext = [page_text(rpdf, p) for p in range(1, rn + 1)]
    stext = [page_text(pdf, p) for p in range(1, sn + 1)]

    slides = exported(deck)
    if len(slides) != sn:
        print(f"note: deck has {len(slides)} exported slides but the PDF has {sn} pages; markers are ignored")
        slides = [{"pin": None, "crop": False, "typos": [], "title": ""} for _ in range(sn)]
    pin_of = {k: s["pin"] for k, s in enumerate(slides) if s["pin"]}
    rw, sw = [words(t) for t in rtext], [words(t) for t in stext]

    def sc(i, j):  # i: reference page, j: Slidev page (0-based)
        if j in pin_of:
            return 100.0 if pin_of[j] == i + 1 else -100.0
        a, b = rw[i], sw[j]
        return sum((a & b).values()) / sum(a.values()) if a else 0.0

    pairs = align(sc, rn, sn, gap=0.3)
    pmap = dict(pairs)
    typo_old = collections.Counter(w.lower() for s in slides for old, _ in s["typos"] for w in WORD.findall(old))

    # render Slidev pages and build compare images
    sdir = os.path.join(rd, "slidev_png")
    shutil.rmtree(sdir, ignore_errors=True)
    os.makedirs(sdir)
    subprocess.run(["pdftoppm", "-png", "-r", "60", pdf, f"{sdir}/p"], check=True)
    from PIL import Image, ImageDraw

    def png(d, n, total):
        width = len(str(total))
        for w in sorted({width, 2, 3}):
            f = f"{d}/p-{n:0{w}d}.png"
            if os.path.exists(f):
                return f
        return None

    rows = []
    cmp_files = []
    for rp in range(1, rn + 1):
        sp = pmap.get(rp)
        missing = words(rtext[rp - 1]) - words(stext[sp - 1]) if sp else words(rtext[rp - 1])
        in_crop = bool(sp and slides[sp - 1]["crop"])
        typo = collections.Counter({w: c for w, c in missing.items() if w in typo_old})
        missing = collections.Counter() if in_crop else missing - typo
        first = next((l.strip() for l in rtext[rp - 1].splitlines() if l.strip()), "")[:60]
        rows.append({"ref_page": rp, "slidev_page": sp, "title": first, "crop": in_crop,
                     "typo_fixed": sorted(typo),
                     "missing": sorted(missing), "missing_count": sum(missing.values())})
        H = 330
        L = Image.open(png(f"{work}/ref", rp, rn)).convert("RGB") if png(f"{work}/ref", rp, rn) else Image.new("RGB", (587, H), "white")
        R = Image.open(png(sdir, sp, sn)).convert("RGB") if sp and png(sdir, sp, sn) else Image.new("RGB", (587, H), (255, 230, 230))
        L = L.resize((int(L.width * H / L.height), H))
        R = R.resize((int(R.width * H / R.height), H))
        g = Image.new("RGB", (L.width + R.width + 24, H + 30), (70, 70, 70))
        g.paste(L, (0, 30))
        g.paste(R, (L.width + 24, 30))
        label = f"ref p{rp}  |  slidev p{sp or '-'}  |  missing words: {sum(missing.values())}"
        ImageDraw.Draw(g).text((8, 8), label, fill="white")
        f = os.path.join(rd, f"cmp-{rp:02d}.png")
        g.save(f)
        cmp_files.append(f)
    for k in range(0, len(cmp_files), 6):
        ims = [Image.open(f) for f in cmp_files[k:k + 6]]
        w, h = max(i.width for i in ims), max(i.height for i in ims)
        sheet = Image.new("RGB", (w * 2, h * 3), (40, 40, 40))
        for j, im in enumerate(ims):
            sheet.paste(im, ((j % 2) * w, (j // 2) * h))
        sheet.save(os.path.join(rd, f"sheet-{k // 6 + 1:02d}.png"))

    crop_pages = {r["ref_page"] for r in rows if r["crop"]}
    deck_missing = (words("\n".join(t for k, t in enumerate(rtext, 1) if k not in crop_pages))
                    - words("\n".join(stext)))
    deck_missing = collections.Counter({w: c for w, c in deck_missing.items() if w not in typo_old})
    brk = re.compile(r"^\s*(pause|break)\b", re.I)
    extra_slidev = [p for p in range(1, sn + 1) if p not in set(pmap.values())]
    extra_breaks = [p for p in extra_slidev if brk.search(slides[p - 1]["title"] or next((l.strip() for l in stext[p - 1].splitlines() if l.strip()), ""))]
    extra_slidev = [p for p in extra_slidev if p not in extra_breaks]
    lint = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint_layout.py"), deck],
                          capture_output=True, text=True).stdout.strip()
    unmatched_ref = [r["ref_page"] for r in rows if r["slidev_page"] is None]
    summary = {"ref_pages": rn, "slidev_pages": sn, "unmatched_ref_pages": unmatched_ref,
               "extra_slidev_pages": extra_slidev, "break_pages": extra_breaks,
               "crop_pages": sorted(crop_pages), "typo_fixes": [t for s in slides for t in s["typos"]],
               "layout_flags": lint.splitlines(), "deck_missing_count": sum(deck_missing.values()),
               "deck_missing": sorted(deck_missing), "pages": rows}
    json.dump(summary, open(os.path.join(rd, "report.json"), "w"), ensure_ascii=False, indent=1)

    out = [f"# Compare round: {os.path.basename(deck)} vs {os.path.basename(rpdf)}", "",
           f"- reference pages: {rn}, Slidev pages: {sn}",
           f"- reference pages without Slidev page: {unmatched_ref or 'none'}",
           f"- Slidev pages without reference page: {extra_slidev or 'none'}",
           f"- break slides (expected without reference page): {extra_breaks or 'none'}",
           f"- crop slides (text is in the image, not counted): reference pages {sorted(crop_pages) or 'none'}",
           f"- typo fixes marked in the deck: {len(summary['typo_fixes'])}",
           f"- words missing in the whole deck: {sum(deck_missing.values())}"
           + (f" ({', '.join(sorted(deck_missing)[:40])}{' ...' if len(deck_missing) > 40 else ''})" if deck_missing else ""),
           "", "| ref | slidev | title | missing words |", "|---|---|---|---|"]
    for r in rows:
        if r["missing_count"] or r["slidev_page"] is None:
            mw = ", ".join(r["missing"][:12]) + (" ..." if len(r["missing"]) > 12 else "")
            out.append(f"| {r['ref_page']} | {r['slidev_page'] or '-'} | {r['title']} | {r['missing_count']}: {mw} |")
    out += ["", "## Layout flags (fix, or give a reason in the round report)", "", "```", lint or "none", "```"]
    out += ["", f"Compare images: {rd}/cmp-NN.png (NN = reference page), sheets: sheet-NN.png"]
    open(os.path.join(rd, "report.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out[:10]))
    print(f"-> {rd}/report.md")


if __name__ == "__main__":
    main()
