"""List layout tricks in a Slidev deck that the briefs forbid or that need a reason.

Usage: python lint_layout.py DECK.md [--allow REGEX]

Flags, per exported slide:
  absolute     `absolute` class or position:absolute (allowed once per slide for a
               source/credit line: lines with class "source" or a credit/source text are skipped)
  offset       top-/left-/right-/bottom- arbitrary offsets (top-[..], left-12, ml-[38%])
  neg-margin   negative margins (-mt-4, -ml-[2rem])
  big-margin   margins of 10 or more (mt-12, !mt-24, mb-16)
  blend        mix-blend-* (often used to hide an overlap)
  fixed-box    fixed width/height boxes in px on divs (w-[600px], h-[300px] on <div>)
  css          <style> blocks inside the deck
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
    ("big-margin", re.compile(r"(?<![\w-])!?m[tblrxy]?-(?:[1-9]\d)(?![\w])")),
    ("blend", re.compile(r"mix-blend-")),
    ("fixed-box", re.compile(r"<div[^>]*class=\"[^\"]*(?<![\w-])[wh]-\[\d+px\]")),
    ("css", re.compile(r"<style")),
]
SKIP_LINE = re.compile(r'class="[^"]*\bsource\b|Quelle|Source|Photo:|Foto:|Credit|CC BY', re.I)


def main():
    deck = sys.argv[1]
    allow = re.compile(sys.argv[sys.argv.index("--allow") + 1]) if "--allow" in sys.argv else None
    found = 0
    for k, s in enumerate(exported(deck), 1):
        hits = []
        for line in s["body"].splitlines():
            if line.lstrip().startswith("<!--"):
                continue
            for name, rx in RULES:
                for m in rx.finditer(line):
                    if name == "absolute" and SKIP_LINE.search(line):
                        continue
                    if allow and allow.search(m.group(0)):
                        continue
                    hits.append(f"{name} `{m.group(0)}`")
        if hits:
            found += len(hits)
            print(f"slide {k} ({s['title'][:40]}): " + ", ".join(sorted(set(hits))))
    print(f"{found} layout flags" if found else "no layout flags")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
