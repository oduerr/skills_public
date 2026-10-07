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

    def scorer(t):
        a = words(t)
        def f(u):
            b = words(u)
            if not a:
                return 0.0
            return sum((a & b).values()) / sum(a.values())
        return f

    pairs = align([scorer(t) for t in rtext], stext, gap=0.3)
    pmap = dict(pairs)

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
        first = next((l.strip() for l in rtext[rp - 1].splitlines() if l.strip()), "")[:60]
        rows.append({"ref_page": rp, "slidev_page": sp, "title": first,
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

    deck_missing = words("\n".join(rtext)) - words("\n".join(stext))
    extra_slidev = [p for p in range(1, sn + 1) if p not in set(pmap.values())]
    unmatched_ref = [r["ref_page"] for r in rows if r["slidev_page"] is None]
    summary = {"ref_pages": rn, "slidev_pages": sn, "unmatched_ref_pages": unmatched_ref,
               "extra_slidev_pages": extra_slidev, "deck_missing_count": sum(deck_missing.values()),
               "deck_missing": sorted(deck_missing), "pages": rows}
    json.dump(summary, open(os.path.join(rd, "report.json"), "w"), ensure_ascii=False, indent=1)

    out = [f"# Compare round: {os.path.basename(deck)} vs {os.path.basename(rpdf)}", "",
           f"- reference pages: {rn}, Slidev pages: {sn}",
           f"- reference pages without Slidev page: {unmatched_ref or 'none'}",
           f"- Slidev pages without reference page: {extra_slidev or 'none'}",
           f"- words missing in the whole deck: {sum(deck_missing.values())}"
           + (f" ({', '.join(sorted(deck_missing)[:40])}{' ...' if len(deck_missing) > 40 else ''})" if deck_missing else ""),
           "", "| ref | slidev | title | missing words |", "|---|---|---|---|"]
    for r in rows:
        if r["missing_count"] or r["slidev_page"] is None:
            mw = ", ".join(r["missing"][:12]) + (" ..." if len(r["missing"]) > 12 else "")
            out.append(f"| {r['ref_page']} | {r['slidev_page'] or '-'} | {r['title']} | {r['missing_count']}: {mw} |")
    out += ["", f"Compare images: {rd}/cmp-NN.png (NN = reference page), sheets: sheet-NN.png"]
    open(os.path.join(rd, "report.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out[:7]))
    print(f"-> {rd}/report.md")


if __name__ == "__main__":
    main()
