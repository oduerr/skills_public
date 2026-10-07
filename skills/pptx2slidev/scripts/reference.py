"""Check that a reference PDF matches the visible slides of a .pptx, and render its pages.

Usage: python reference.py OUTDIR/slides.json reference.pdf OUTDIR [--render] [--break-pattern REGEX]

The reference PDF should be exported from PowerPoint itself (it shows the real
fonts, WMF graphics and formulas). If there is none, make one with LibreOffice
(see SKILL.md), but say so in the report.

Prints a match report and writes OUTDIR/reference.json:
  {"pages": N, "slides": M, "match": "ok" | "mismatch", "map": [[slide, page], ...], "problems": [...]}
Pages are matched to slides by title text (pdftotext per page), in order, so a
PDF that is older or newer than the .pptx shows up as missing or extra pages.
Break slides (title matches --break-pattern, default "^(Pause|Break)") are listed
separately and do not cause a mismatch: they are often added after the lecture,
after the PDF was made. They are taken over as they are (they record where the
break was) and need no layout work.
With --render, pages are rendered to OUTDIR/ref/p-NN.png (60 dpi, for compare
images) and OUTDIR/ref_hi/p-NN.png (200 dpi, for crops).
Needs: poppler (pdftotext, pdftoppm, pdfinfo).
"""
import json
from pathlib import Path
import os
import re
import subprocess
import sys
from difflib import SequenceMatcher


def norm(s):
    return " ".join(re.findall(r"\w+", s.lower()))


def page_count(pdf):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))


def page_text(pdf, n):
    return subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), "-layout", pdf, "-"],
                          capture_output=True, text=True).stdout


def score(slide, text):
    """How well a page text fits a slide: title found at the top, plus word overlap.
    Slides without text (picture slides) fit pages with (almost) no text."""
    t = norm(slide["title"])
    head = norm(" ".join(text.splitlines()[:8]))
    if not norm(slide["text"]) and len(norm(text).split()) <= 3:
        return 0.9
    s = 0.0
    if t and t in head:
        s += 1.0
    elif t:
        s += SequenceMatcher(None, t, head[: len(t) + 40]).ratio() * 0.8
    a, b = set(norm(slide["text"]).split()), set(norm(text).split())
    if a:
        s += len(a & b) / len(a)
    return s


def align(score, S, P, gap=0.6):
    """Order-preserving alignment of S items to P pages.
    score(i, j) -> float for item i and page j (0-based). Returns [(item_no, page_no)] (1-based).
    Items or pages may stay unmatched."""
    INF = -1e9
    best = [[INF] * (P + 1) for _ in range(S + 1)]
    back = [[None] * (P + 1) for _ in range(S + 1)]
    best[0] = [0.0] * (P + 1)
    for j in range(1, P + 1):
        back[0][j] = ("skip_page", 0, j - 1)
    for i in range(1, S + 1):
        best[i][0] = 0.0
        back[i][0] = ("skip_slide", i - 1, 0)
        for j in range(1, P + 1):
            cands = [
                (best[i - 1][j - 1] + score(i - 1, j - 1) - gap, ("match", i - 1, j - 1)),
                (best[i - 1][j], ("skip_slide", i - 1, j)),
                (best[i][j - 1], ("skip_page", i, j - 1)),
            ]
            best[i][j], back[i][j] = max(cands, key=lambda c: c[0])
    pairs, i, j = [], S, P
    while i > 0 and j > 0:
        kind, pi, pj = back[i][j]
        if kind == "match":
            pairs.append((i, j))
        i, j = pi, pj
    return pairs[::-1]


def slide_box(pdf, ratio=None):
    """Where the slide sits on the PDF page (PowerPoint and LibreOffice put a 4:3 or 16:9
    slide onto A4 with margins). Estimated from the union of non-white pixels over all
    pages, so every agent does not have to measure it again. Returns [x0, y0, x1, y1] in pt."""
    try:
        import tempfile
        from PIL import Image, ImageChops
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["pdftoppm", "-png", "-r", "20", pdf, f"{d}/p"], check=True, capture_output=True)
            files = sorted(Path(d).glob("p-*.png"))
            box = None
            for f in files:
                im = Image.open(f).convert("L")
                bg = Image.new("L", im.size, 255)
                b = ImageChops.difference(im, bg).point(lambda v: 255 if v > 12 else 0).getbbox()
                if b:
                    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
            if not box:
                return None
            scale = 72 / 20
            return [round(v * scale, 1) for v in box]
    except Exception:
        return None


def main():
    index_file, pdf, out = sys.argv[1:4]
    render = "--render" in sys.argv
    brk = sys.argv[sys.argv.index("--break-pattern") + 1] if "--break-pattern" in sys.argv else r"\b(pause|break)\b"
    slides = json.load(open(index_file))
    n = page_count(pdf)
    texts = [page_text(pdf, p) for p in range(1, n + 1)]

    S = len(slides)
    pairs = align(lambda i, j: score(slides[i], texts[j]), S, n)

    matched_s = {s for s, _ in pairs}
    matched_p = {p for _, p in pairs}
    problems, breaks = [], []
    for s in slides:
        is_break = bool(re.search(brk, s["title"], re.I)) and len(s["title"]) < 70
        if is_break:
            breaks.append({"slide": s["slide"], "original": s["original"], "title": s["title"],
                           "in_pdf": s["slide"] in matched_s})
        if s["slide"] not in matched_s and not is_break:
            problems.append(f"slide {s['slide']} '{s['title']}' has no page in the PDF")
    for p in range(1, n + 1):
        if p not in matched_p:
            first = next((l.strip() for l in texts[p - 1].splitlines() if l.strip()), "")
            problems.append(f"page {p} '{first[:60]}' has no slide in the .pptx")
    # a slide "missing" and a page "extra" with the same title = order differs, not content
    miss = {norm(s["title"]): s["slide"] for s in slides if s["slide"] not in matched_s and s["title"]}
    for p in range(1, n + 1):
        if p not in matched_p:
            head = norm(" ".join(texts[p - 1].splitlines()[:6]))
            for t, sno in miss.items():
                if t and t in head:
                    problems.append(f"slide {sno} '{t[:40]}' looks like page {p}: order differs between .pptx and PDF")
    match = "ok" if not problems else "mismatch"
    warn = []
    if slides and slides[0].get("source_mtime") and os.path.getmtime(pdf) + 60 < slides[0]["source_mtime"]:
        import datetime
        d = lambda t: datetime.date.fromtimestamp(t).isoformat()
        warn.append(f"the PDF ({d(os.path.getmtime(pdf))}) is older than the .pptx ({d(slides[0]['source_mtime'])}): "
                    "it may miss later changes even where pages match")

    os.makedirs(out, exist_ok=True)
    box = slide_box(pdf)
    json.dump({"pdf": os.path.abspath(pdf), "pages": n, "slides": S, "match": match,
               "map": pairs, "problems": problems, "warnings": warn, "break_slides": breaks,
               "slide_box_pt": box},
              open(f"{out}/reference.json", "w"), indent=1)
    print(f"reference: {pdf}\n  {n} pages, {S} visible slides, match: {match}")
    for w in warn:
        print("  WARNING", w)
    if box:
        print(f"  slide box on the page (pt, x0 y0 x1 y1): {box} — crops: see crop_ref.py")
    for x in problems[:30]:
        print("  -", x)
    if len(problems) > 30:
        print(f"  ... {len(problems) - 30} more in reference.json")
    if breaks:
        print(f"  break slides (expected; often not in the PDF, taken over as they are): "
              + "; ".join(f"slide {b['slide']} '{b['title']}'" + ("" if b["in_pdf"] else " (not in PDF)") for b in breaks))

    if render:
        for d, dpi in (("ref", 60), ("ref_hi", 200)):
            os.makedirs(f"{out}/{d}", exist_ok=True)
            subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, f"{out}/{d}/p"], check=True)
        print(f"  rendered to {out}/ref/ and {out}/ref_hi/ (p-NN.png = PDF page NN)")


if __name__ == "__main__":
    main()
