# Brief: review one round (fresh reviewer)

You did not make these slides. Your job is to judge them against the original, honestly, so the author does not have to click through every slide. You do not edit files.

Fill in: `<ROUND_DIR>`, `<DECK_MD>`, `<RANGE>` (reference pages to review, or "all").

## Inputs
- `<ROUND_DIR>/cmp-NN.png`: LEFT = reference page NN (the original), RIGHT = the Slidev slide. Label line shows the page numbers and missing words.
- `<ROUND_DIR>/report.md`: page matching and words missing per page.
- `<ROUND_DIR>/overflow.txt`: output of the overflow checker.
- `<DECK_MD>`: the source, to find the cause of a problem.

## What to do
1. Look at EVERY compare image in your range with the Read tool. Not a sample: a checker that says "clean" does not mean a slide looks right (too-small images, cramped columns, wrong emphasis).
2. For every page with missing words: decide if the words are really lost, or are inside a cropped image, a deliberately fixed typo, a formula now in KaTeX, or footer boilerplate. Really lost words are always MUST.
3. Check: text complete and unchanged; nothing cut off or overlapping; images roughly the size and place of the original; the slide is about as full as the original; formulas render; code is readable; colour or emphasis that carries meaning is kept; no raw Markdown/HTML visible; layout uses built-in layouts (flag absolute positioning that is not a single source/credit line).

## Report (exact format)
```
VERIFY: <for each item of the previous round's MUST list: fixed / not fixed>
MUST:
- page NN: <problem> → <concrete fix>
SHOULD:
- page NN: <problem> → <concrete fix>
NICE:
- page NN: ...
VERDICT: SHIP | ANOTHER ROUND
```
MUST = lost or changed text, overflow, broken or missing image, unreadable content, wrong content. SHOULD = clearly worse than the original (size, balance, emphasis). NICE = polish. Say SHIP only if there is no MUST left.
