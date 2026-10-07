# Brief: review one round (fresh reviewer)

You did not make these slides. Your job is to judge them against the original, honestly, so the author does not have to click through every slide. You do not edit files.

Fill in: `<ROUND_DIR>`, `<DECK_MD>`, `<RANGE>` (reference pages to review, or "all").

## Inputs
- `<ROUND_DIR>/cmp-NN.png`: LEFT = reference page NN (the original), RIGHT = the Slidev slide. Label line shows the page numbers and missing words.
- `<ROUND_DIR>/report.md`: page matching and words missing per page.
- `<ROUND_DIR>/overflow.txt`: output of the overflow checker.
- `<DECK_MD>`: the source, to find the cause of a problem.

## Tools
For measurements (pixel checks, crops), use the skill's venv: `~/.local/share/pptx2slidev/venv/bin/python` (has Pillow).

## What to do
1. Look at EVERY compare image in your range with the Read tool. For each page, write one line with a concrete detail you saw on it (e.g. "p12: table with 4 rows, header blue in the original, plain in Slidev"). This shows you really looked; a fast review that only repeats the checker is worth nothing. Not a sample: a checker that says "clean" does not mean a slide looks right (too-small images, cramped columns, wrong emphasis).
2. For every page with missing words: decide if the words are really lost, or are inside a cropped image, a deliberately fixed typo, a formula now in KaTeX, or footer boilerplate. Really lost words are always MUST.
3. Read the "Layout flags" section of report.md: every flag is MUST (fix) unless the slide clearly needs it; say which. Look at the info lines too: spacing that only shrank since the last round, and many different arbitrary text sizes, are SHOULD.
4. **Click states and covers**: for every page whose pptx slide has `CLICK` / `COVER` lines in dump.md (and every page `report.md` lists under "click steps missing"), check that answers are hidden in the first state and shown after the clicks — open the slide in a `--with-clicks` export or the browser (`/N?clicks=0` and `?clicks=99` on a private server). A visible answer is MUST.
5. **Pictures**: compare with the original — cropped like it (no extra browser tabs, data or answers), rotated like it, same aspect. Read `images.txt`.
6. Look for stray lines and borders (table row lines running through labels or arrows), lost bold/colour in headers, and slides much emptier than the original.
7. Check: text complete and unchanged; nothing cut off or overlapping; images roughly the size and place of the original; the slide is about as full as the original; formulas render; code is readable; colour or emphasis that carries meaning is kept; no raw Markdown/HTML visible; layout uses built-in layouts (flag absolute positioning that is not a single source/credit line).

## Report (exact format)
```
SEEN:
- page NN: <one concrete detail>
VERIFY: <for each item of the previous round's MUST list: fixed / not fixed>
MUST:
- page NN: <problem> → <concrete fix>
SHOULD:
- page NN: <problem> → <concrete fix>
NICE:
- page NN: ...
VERDICT: SHIP | ANOTHER ROUND
```
MUST = visible answers (lost click steps or covers), uncropped pictures, lost, added or changed text, clipped content, overflow, broken or missing image, unreadable content, wrong content. SHOULD = clearly worse than the original (size, balance, emphasis). NICE = polish. Say SHIP only if there is no MUST left.
