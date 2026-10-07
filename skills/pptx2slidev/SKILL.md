---
name: pptx2slidev
description: Convert PowerPoint (.pptx) lecture or talk decks into Slidev Markdown decks that look like the original, with a check loop against a reference PDF (page matching, lost-words check, side-by-side compare images, fresh reviewer) and image provenance records. Use this skill whenever the user wants to move slides from PowerPoint to Slidev, convert or port a .pptx (or "this week's lecture", "the remaining decks") to Markdown slides, re-check or polish an earlier PPTX→Slidev conversion, or compare a Slidev deck with the old PowerPoint PDF — even if they do not say "Slidev" but the project already uses it.
---

# PowerPoint → Slidev

Converting slides is easy; converting them so the author can teach from them without surprises is not. What went wrong in earlier conversions: text got shortened by fixer agents, agents reported fixes they had not made, absolutely positioned boxes drifted over content, a font change late in the process created new overflows, text inside formulas was not extracted, and screenshots taken on the author's running presentation server moved the author's slides. This skill is built around those lessons: one strong agent per deck, a reference PDF as ground truth, measurable checks, and a fresh reviewer who looks at every slide.

## Phase 0: settle the setup (ask before building anything)

Collect these from the request, the project (README, CLAUDE.md, existing decks, `style.css`), or ask the user in one short message. Do not start converting until they are clear.

1. **Source and target**: which .pptx files, which Slidev project and file names.
2. **Aspect ratio**: compare the .pptx (dump.md header: ratio 1.333 = 4:3, 1.778 = 16:9) with the projector and the project's other decks. Converting 4:3 into 16:9 changes every slide: about a quarter less height, so content must shrink or reflow, which drives most layout rounds. Keeping 4:3 converts almost 1:1 but leaves side bars on a wide projector. Ask the user if the project does not say; record the choice in the project settings.
3. **Style**: theme, fonts, base size, existing CSS helpers or layouts in the project. Decide this FIRST — changing fonts or base size after the layout rounds causes new overflows everywhere. Default when the project has nothing: default theme, built-in layouts, no custom CSS.
4. **Reference PDF** (see below).
5. **Effort**, set by the user, default `normal`:
   - `quick`: one conversion pass and one check round, report the rest.
   - `normal`: loop up to 5 rounds.
   - `thorough`: loop up to 10 rounds.
   The user may also give a number ("up to 7 rounds").
6. **Agents**: the user says how many ("use four agents, one per deck"). If not said and there is more than one deck, ask. Split by deck, not by slide range: one agent who owns a whole deck keeps it consistent. One deck = do it yourself or with one agent.
7. **Project settings**: look for a section "Slidev conversion" in the project README (or CLAUDE.md). It records what the next run needs: style, the `--ignore` selectors for decorative layouts in the overflow checker (e.g. `--ignore=.htwg-cover`), image folders, where reference PDFs live. If it is missing, write it at the end of the run (Phase 4), so the next run does not rediscover it.
8. **Image folders**: where deck images go (`public/<deck>/`) and the internal folder for images with unclear rights (default `public/_intern/<deck>/`, one subfolder per deck, so it stays clear which deck an internal image belongs to).

## Phase 1: extract and check the reference

Set up once: a Python venv with `python-pptx` and `Pillow` in a place that survives a reboot (default `~/.local/share/pptx2slidev/venv`; not `/tmp`):
`python3 -m venv ~/.local/share/pptx2slidev/venv && ~/.local/share/pptx2slidev/venv/bin/pip install python-pptx Pillow`. Also: poppler (`pdftotext`, `pdftoppm`, `pdfinfo`); a Slidev install with `playwright-chromium` (the scripts look in `$SLIDEV_RUNTIME`, the deck's `node_modules`, then `~/.local/share/slidev-runtime`). Use a work folder outside the repo, one per deck (`WORK`).

```bash
PY=~/.local/share/pptx2slidev/venv/bin/python
$PY scripts/extract.py deck.pptx $WORK            # dump.md, slides.json, media/
$PY scripts/reference.py $WORK/slides.json ref.pdf $WORK --render
```

**The reference PDF** is the ground truth for every comparison. Best is a PDF the author exported from PowerPoint (real fonts, WMF graphics, formulas). Ask where they keep these if the project does not say.

`reference.py` matches PDF pages to the visible slides by title and text and reports `match: ok` or `mismatch` (a PDF older or newer than the .pptx shows as missing or extra pages).

**Break slides** (title starts with "Pause" or "Break"; change with `--break-pattern`) are listed separately and never cause a mismatch: authors often add them after the lecture, when no new PDF is made. Take them over as they are — title and text verbatim, including times and semesters, no layout work. They record where the break was, which is useful history.

Then:
- `ok` → go on.
- `mismatch` or no PDF → **ask the user to export a fresh PDF from PowerPoint** and give them the problem list — also when the mismatch looks small (e.g. only a break slide is missing). Do not decide this yourself: the user knows which version is current, and an export takes them a minute. You may suggest "continue with the old PDF" as an option in the same question. Only if they cannot or say "skip", make one with LibreOffice (`soffice --headless --convert-to pdf deck.pptx`, with a timeout; if a pptx skill with a `soffice.py` wrapper is installed, use that — bare soffice can hang) and note in the final report that the reference is a LibreOffice render.

Hidden slides are not in the PDF and not in `slides.json`; that is correct. Page numbers and slide numbers differ, so always go through `reference.json`.

## Phase 2: convert

Give each converter agent `references/convert_brief.md` with the placeholders filled in (or follow it yourself). Use Opus or Sonnet; do not use Haiku for converting or fixing — it shortened text and faked "no changes" in earlier runs. The core rules, with the reasons in the brief:
- Never shorten, paraphrase or translate text.
- Built-in layouts first; no absolute positioning except one source/credit line per slide; no custom grid divs.
- Crop what cannot be rebuilt from the 200-dpi reference page.
- Provenance for every image (comment in the deck + row in `PROVENANCE.md`), see `references/provenance.md`. Unclear rights count as not free → internal folder.

## Phase 3: the check loop

Each round, per deck:

```bash
R=$WORK/round-NN
$PY scripts/compare.py DECK.md $WORK $R               # export, page match, missing words, layout flags, cmp-NN.png, sheets
node scripts/check_overflow.mjs DECK.md > $R/overflow.txt  # add --ignore=<selectors> from the project settings
$PY scripts/provenance.py DECK.md > $R/provenance.txt
```

Both scripts start their own private server (localhost, random port). Never take screenshots on a server the user is presenting from: Slidev syncs navigation, so you would move their slides.

Then a **fresh reviewer** (an agent that did not make the slides, or you with fresh eyes if working alone) follows `references/review_brief.md`: it looks at every compare image, explains every missing word, and ends with `VERDICT: SHIP | ANOTHER ROUND` plus a MUST/SHOULD/NICE list. A **fixer** follows `references/fix_brief.md` for the MUST and SHOULD items. Look at a few compare images yourself every round — agents' self-reports overstate.

`compare.py` reads marker comments in the deck (the converter writes them, see the convert brief): `<!-- ref: pNN -->` pins a slide to a reference page, `<!-- ref: pNN crop -->` marks a slide whose text is inside a cropped image, `<!-- typo: old -> new -->` marks a deliberate typo fix. Crops and typo fixes are then not counted as missing words, so the count can really reach zero. It also runs `lint_layout.py`: absolute positioning, offsets, negative or big margins, `mix-blend`, fixed boxes. Every flag must be fixed or listed with a reason. Why: in an earlier run the fixer added `!mt-24`, `-mt-10` and `mix-blend-multiply` against the brief and did not report it; only a look at the slides found it.

**Stop** when all hold, or when the round limit from Phase 0 is reached:
1. `overflow.txt` has no `overflow`, `NOT RENDERED` or `broken image` lines;
2. `report.md` has no really lost words (remaining ones explained by the reviewer: footer, page numbers) and no unexplained layout flags;
3. the reviewer says SHIP;
4. `provenance.py` reports no problems.

## Phase 4: final report and handover

1. Run one last `compare.py` round as the final PDF-against-PDF check.
2. Give the user:
   - the contact sheets (`sheet-NN.png`: reference left, Slidev right, all pages) — the fastest way for them to see everything;
   - a short report: slide counts; deliberate differences and why (crops, formulas rewritten in KaTeX, layout changes); exceptions to the layout rules with reasons; what is still open if the round limit was hit; whether the reference was a LibreOffice render;
   - a section **"For you to decide"**: every typo fix (old → new), stale content that was kept verbatim (old semesters, dates, calendars, break times), visual elements that were dropped (backgrounds, decorations the project has no class for), images with unclear rights.
3. If the project settings section was missing or incomplete, add it to the project README (style, `--ignore` selectors, image folders, reference PDF location).
4. Commit only after the user agrees.

## Pitfalls (short)

- `text-xl` is 20 px — smaller than the ~21 px base, not bigger.
- Base Slidev CSS beats utility classes on tables and blockquotes; use the `!` prefix. The default theme draws a grey line under every table row (on `tr`, not `td`): an HTML table used for layout (arrows, labels beside a table) needs `[&_tr]:border-0` or `class="!border-0"` on each `tr`, else lines cross the whole slide.
- Typographic quotes in `class=”…”` silently disable the class.
- The default theme greys out the first paragraph after a title; the project may need one CSS line.
- KaTeX does not render inside raw HTML paragraphs.
- `<-` in R code may become a ligature arrow with some fonts.
- Do not `npm install` inside synced folders (iCloud, Dropbox); use a shared Slidev runtime.
- Speaker notes become HTML comments at the end of the slide; keep them.

## Files

- `scripts/extract.py` — PPTX → dump.md, slides.json, media/
- `scripts/reference.py` — check and render the reference PDF
- `scripts/compare.py` — one check round (export, page match, missing words, compare images, report)
- `scripts/check_overflow.mjs` — overflow, broken images, small text, underfilled slides
- `scripts/provenance.py` — image provenance check
- `scripts/lint_layout.py` — layout tricks per slide (run by compare.py)
- `scripts/deck.py` — reads a Slidev deck into exported slides and marker comments (`python scripts/deck.py DECK.md` lists them)
- `references/convert_brief.md`, `review_brief.md`, `fix_brief.md` — briefs for agents
- `references/provenance.md` — provenance format and rules
