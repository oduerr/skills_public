"""List layout tricks in a Slidev deck that the briefs forbid or that need a reason.

Usage: python lint_layout.py DECK.md [--allow REGEX]

Flags, per exported slide:
  absolute     `absolute` class or position:absolute (allowed once per slide for a
               source/credit line: lines with class "source" or a credit/source text are skipped)
  offset       top-/left-/right-/bottom- arbitrary offsets (top-[..], left-12, ml-[38%])
  neg-margin   negative margins (-mt-4, -ml-[2rem])
  big-margin   vertical margins of 10 or more (mt-12, !mt-24, mb-16)
  big-indent   horizontal margins of 16 or more (ml-24, mx-36); a small indent
               like the original (ml-4 … ml-12) is fine, but a nested list or a
               built-in layout is better
  blend        mix-blend-* (often used to hide an overlap)
  fixed-box    fixed width/height boxes in px on divs (w-[600px], h-[300px] on <div>)
  css          <style> blocks inside the deck
  layout-table an HTML table used for layout (cells with border-0) without
               [&_tr]:!border-0: the theme's grey row lines run through it
Also prints (info, not failing): all spacing utilities per slide, and all
arbitrary text sizes (text-[1.55rem]) with their slides. Compare these lines
between rounds: a fixer that only shrinks a margin below a threshold
(mt-16 -> mt-8) has not fixed anything; many different sizes make the deck uneven.
Only class/style attributes, HTML tags, {mdc} attributes and `class:` lines are
checked, never slide text or code.
Why: these tricks make a slide look right once and break on the next change of
text, font or size; earlier fixers added them silently. Each flagged item must be
fixed or listed as an exception with a reason in the round report.
Exit code 1 if anything is flagged.
"""
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from deck import exported  # noqa: E402

RULES = [
    ("absolute", re.compile(r"(?<![\w-])absolute(?![\w-])|position:\s*absolute")),
    ("offset", re.compile(r"(?<![\w-])!?(?:top|left|right|bottom|inset)-(?:\[[^\]]+\]|\d+)|(?<![\w-])!?m[lr]-\[\d+%\]")),
    ("neg-margin", re.compile(r"(?<![\w])!?-m[tblrxy]?-(?:\[[^\]]+\]|\d+)")),
    ("big-margin", re.compile(r"(?<![\w-])!?m[tby]?-(?:[1-9]\d)(?![\w])")),
    ("big-indent", re.compile(r"(?<![\w-])!?m[lrx]-(?:1[6-9]|[2-9]\d)(?![\w])")),
    ("blend", re.compile(r"mix-blend-")),
    ("fixed-box", re.compile(r"<div[^>]*class=\"[^\"]*(?<![\w-])[wh]-\[\d+px\]")),
    ("css", re.compile(r"<style")),
]
CODE_SEGMENTS = re.compile(r"<[^>]+>|\{[^}\n]*\}|^\s*class:.*$", re.M)  # tags, {mdc attrs}, class: frontmatter
SPACING = re.compile(r"(?<![\w-])!?-?[mp][tblrxy]?-(?:\[[^\]]+\]|\d+)(?![\w])")
SIZE = re.compile(r"(?<![\w-])!?text-\[[\d.]+(?:rem|em|px)\]")
SKIP_LINE = re.compile(r'class="[^"]*\bsource\b|Quelle|Source|Photo:|Foto:|Credit|CC BY', re.I)


def main():
    deck = sys.argv[1]
    allow = re.compile(sys.argv[sys.argv.index("--allow") + 1]) if "--allow" in sys.argv else None
    found = 0
    spacing, sizes = {}, {}
    for k, s in enumerate(exported(deck), 1):
        hits = []
        body = re.sub(r"<!--.*?-->", " ", s["body"], flags=re.S)
        body = re.sub(r"^(```|~~~).*?^\1", " ", body, flags=re.S | re.M)  # code blocks
        for line in body.splitlines():
            segs = " ".join(m.group(0) for m in CODE_SEGMENTS.finditer(line))
            if not segs:
                continue
            for m in SPACING.finditer(segs):
                spacing.setdefault(k, []).append(m.group(0))
            for m in SIZE.finditer(segs):
                sizes.setdefault(m.group(0).lstrip("!"), []).append(k)
            for name, rx in RULES:
                for m in rx.finditer(segs):
                    if name == "absolute" and SKIP_LINE.search(line):
                        continue
                    if allow and allow.search(m.group(0)):
                        continue
                    hits.append(f"{name} `{m.group(0)}`")
        for t in re.finditer(r"<table\b[^>]*>.*?</table>", body, flags=re.S | re.I):
            tbl = t.group(0)
            if re.search(r'class="[^"]*\bborder-0\b', tbl) and not re.search(r"\[&_tr\]:!?border-0|<tr[^>]*!border-0", tbl):
                hits.append("layout-table `<table>` with border-0 cells but no [&_tr]:!border-0 (theme row lines will show)")
        if hits:
            found += len(hits)
            print(f"slide {k} ({s['title'][:40]}): " + ", ".join(sorted(set(hits))))
    print(f"{found} layout flags" if found else "no layout flags")
    n_sp = sum(len(v) for v in spacing.values())
    print(f"info: {n_sp} spacing utilities on {len(spacing)} slides"
          + (": " + "; ".join(f"{k}: {' '.join(v)}" for k, v in spacing.items()) if spacing else ""))
    if sizes:
        print(f"info: {len(sizes)} different arbitrary text sizes: "
              + "; ".join(f"{z} on {sorted(set(v))}" for z, v in sorted(sizes.items())))
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
