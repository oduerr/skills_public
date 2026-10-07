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
    """How well a page text fits a slide: title found at the top, plus word overlap."""
    t = norm(slide["title"])
    head = norm(" ".join(text.splitlines()[:8]))
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


def main():
    index_file, pdf, out = sys.argv[1:4]
    render = "--render" in sys.argv
    brk = sys.argv[sys.argv.index("--break-pattern") + 1] if "--break-pattern" in sys.argv else r"^\s*(pause|break)\b"
    slides = json.load(open(index_file))
    n = page_count(pdf)
    texts = [page_text(pdf, p) for p in range(1, n + 1)]

    S = len(slides)
    pairs = align(lambda i, j: score(slides[i], texts[j]), S, n)

    matched_s = {s for s, _ in pairs}
    matched_p = {p for _, p in pairs}
    problems, breaks = [], []
    for s in slides:
        is_break = bool(re.search(brk, s["title"], re.I))
        if is_break:
            breaks.append({"slide": s["slide"], "original": s["original"], "title": s["title"],
                           "in_pdf": s["slide"] in matched_s})
        if s["slide"] not in matched_s and not is_break:
            problems.append(f"slide {s['slide']} '{s['title']}' has no page in the PDF")
    for p in range(1, n + 1):
        if p not in matched_p:
            first = next((l.strip() for l in texts[p - 1].splitlines() if l.strip()), "")
            problems.append(f"page {p} '{first[:60]}' has no slide in the .pptx")
    match = "ok" if not problems else "mismatch"

    os.makedirs(out, exist_ok=True)
    json.dump({"pdf": os.path.abspath(pdf), "pages": n, "slides": S, "match": match,
               "map": pairs, "problems": problems, "break_slides": breaks},
              open(f"{out}/reference.json", "w"), indent=1)
    print(f"reference: {pdf}\n  {n} pages, {S} visible slides, match: {match}")
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
