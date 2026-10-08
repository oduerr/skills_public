---
name: pptx2slidev
description: Convert PowerPoint (.pptx) lecture or talk decks into Slidev Markdown decks that look like the original, with a check loop against a reference PDF (page matching, lost-words check, click steps, cropped pictures, side-by-side compare images, fresh reviewer) and image provenance records; also re-checks decks that were converted earlier. Use this skill whenever the user wants to move slides from PowerPoint to Slidev, convert or port a .pptx (or "this week's lecture", "the remaining decks") to Markdown slides, re-check or polish an earlier PPTX→Slidev conversion, or compare a Slidev deck with the old PowerPoint PDF — even if they do not say "Slidev" but the project already uses it.
---

# PowerPoint → Slidev

> **Status: beta (2026-10).** Used on 22 lecture decks (about 1500 slides, German and English, 4:3 → 16:9); a regression test with 25 known failures passes. Every real run so far still found a new kind of silent error, so look at the results yourself (contact sheets, click states) before you teach from them. Feedback welcome.

Converting slides is easy; converting them so the author can teach from them without surprises is not. In real runs (WAST 14 decks, ML/DL 8 decks) the failures that mattered were silent: answers visible because click animations or cover boxes were lost, private browser tabs visible because a PowerPoint crop was ignored, formula lines cut off inside a column, slides swallowed by the parser, provenance comments shown as speaker notes, fixer agents shortening text or reporting fixes they had not made. Every deck still came out as "SHIP" from its reviewer — the errors were found by measurable checks and by the main agent looking itself. So this skill is built on: the PowerPoint file and a reference PDF as ground truth, scripts that measure, a fresh reviewer, and spot checks by the main agent.

Read `references/pitfalls.md` before converting; give it to every converter and fixer.

## Phase 0: settle the setup (ask before building anything)

Collect these from the request, the project (README section "Slidev conversion", CLAUDE.md, existing decks, `style.css`), or ask the user in ONE short message. Do not start converting until they are clear.

1. **Mode**: `convert` (new deck from .pptx) or `check` (a deck converted earlier, see "Check mode" below).
2. **Source and target**: which .pptx files (ask when two versions exist, e.g. `_fuer_2026`, `_with_video`), which Slidev project and file names.
3. **Aspect ratio**: compare the .pptx (dump.md header: 1.333 = 4:3, 1.778 = 16:9) with the projector and the project's other decks. 4:3 into 16:9 means about a quarter less height: rebuild (e.g. two columns), do not squeeze. Record the choice in the project settings.
4. **Style**: theme, fonts, base size, slide classes (exercise, code, blackboard …). Decide FIRST — changing fonts after the layout rounds causes new overflows everywhere. Default: default theme, built-in layouts, no custom CSS.
5. **Reference PDFs** (Phase 1). Check all decks at once and ask the user once.
6. **Effort** (user may override): `quick` = one pass + one check round; `normal` = up to 5 rounds (default); `thorough` = up to 10; or a number.
7. **Agents**: the user says how many ("four agents"). If not said and there is more than one deck, ask. One agent per deck (see Orchestration).
8. **Project settings**: a README section "Slidev conversion" records style, ratio, slide classes, `--ignore` selectors for the overflow checker (e.g. `--ignore=.my-cover`), image folders, reference PDF location, `vite.config.ts` needs. If missing, write it at the end of the run.
9. **Image folders**: `public/<deck>/` and, for images that are not free, `public/_intern/<deck>/`.

## Phase 1: extract and check the reference

Set up once: a venv that survives a reboot (`~/.local/share/pptx2slidev/venv`, not `/tmp`): `python3 -m venv ~/.local/share/pptx2slidev/venv && ~/.local/share/pptx2slidev/venv/bin/pip install python-pptx Pillow`. Also poppler (`pdftotext`, `pdftoppm`, `pdfinfo`, `pdffonts`) and a Slidev install with `playwright-chromium` (the scripts look in `$SLIDEV_RUNTIME`, the deck's `node_modules`, then `~/.local/share/slidev-runtime`). One work folder per deck, outside the repo; each agent has its own folder and never writes helper scripts into a shared one (in a run, one agent overwrote another's helper and mapped all slides wrong).

```bash
PY=~/.local/share/pptx2slidev/venv/bin/python
$PY scripts/extract.py deck.pptx $WORK      # dump.md, slides.json, pictures.json, media/
$PY scripts/reference.py $WORK/slides.json ref.pdf $WORK --render
```

`dump.md` lists per visible slide: shapes with positions, text, a `raw text:` line (authoritative, includes formula text), pictures with **CROPPED / ROTATED / STRETCHED** notes (media files are already cropped; `*.raw.*` files must not be used), **COVER** shapes (white boxes over pictures, often hiding an answer until a click), **MARK** shapes (circles, arrows drawn on pictures), **CLICK n:** lines (what appears or disappears per click), notes and links.

**The reference PDF** is the ground truth. Best is a PDF the author exported from PowerPoint. `reference.py` matches pages to slides and reports `match: ok | mismatch`, warns when the PDF is older than the .pptx, finds reordered slides, and stores `slide_box_pt` (where the slide sits on the page). **Break slides** (title contains "Pause"/"Break") never cause a mismatch: they are often added after the lecture. Take them over verbatim (times, semesters), no layout work.

- `ok` → go on.
- `mismatch` or no PDF → ask the user ONCE for all decks to export fresh PDFs from PowerPoint, with the problem lists; offer "use LibreOffice" in the same question. If the user said beforehand not to wait, render with LibreOffice (`soffice --headless --convert-to pdf`, with a timeout; prefer a pptx skill's `soffice.py` wrapper if installed) and say so in the report. LibreOffice specifics are in `references/pitfalls.md`.

## Phase 2: convert

Give each converter `references/convert_brief.md` (placeholders filled in), `references/pitfalls.md` and the run's `lessons.md`. Use Opus or Sonnet, not Haiku (it shortened text and faked "no changes"). Core rules, reasons in the brief: never add, shorten, paraphrase or translate text; reproduce click steps, covers and crops; built-in layouts first; provenance for every image, at the top of the slide.

A test round before round 1 (`round-00`) is fine.

## Phase 3: the check loop

Each round, per deck:

```bash
R=$WORK/round-NN
$PY scripts/compare.py DECK.md $WORK $R                 # export, build errors, KaTeX fonts, page match, lost words,
                                                         # click steps, layout lint, compare images, sheets
node scripts/check_overflow.mjs DECK.md > $R/overflow.txt   # --ignore=<selectors>; overflow, CLIPPED, UNDER ICON
$PY scripts/check_images.py DECK.md $WORK > $R/images.txt   # raw (uncropped) pictures, rotation, stretching
$PY scripts/provenance.py DECK.md > $R/provenance.txt
```

All scripts use their own private server; never take screenshots on a server the user presents from (Slidev syncs navigation).

`compare.py` reads marker comments in the deck (written by the converter, at the top of the slide): `<!-- ref: pNN -->` pins a slide to a page, `<!-- ref: pNN crop -->` the slide is a crop of that page, `<!-- ref: pNN partial -->` part of it is, `<!-- ref: none -->` a new slide, `<!-- typo: old -> new -->` a deliberate typo fix. It normalises ligatures, URLs and hyphenation, counts text in `v-click` blocks, and lists missing click steps.

Then a **fresh reviewer** follows `references/review_brief.md` (every compare image, click states, covers, missing words, layout flags) and a **fixer** follows `references/fix_brief.md`.

**Spot checks by the main agent are mandatory** after every fix round: open at least the slides the fixer touched and every slide with click steps, covers or crops, in the compare images and, for click steps, in the browser or a `--with-clicks` export. In the runs, self-reports said "fixed" for lines that were still missing, and reviewers called an unrotated diagram "NICE".

**Stop** when all hold, or at the round limit:
1. `compare.py`: no build errors, KaTeX fonts present, no missing click steps, no really lost words (rest explained: footer, page numbers), no unexplained layout flags;
2. `overflow.txt`: no `overflow`, `CLIPPED`, `UNDER ICON`, `NOT RENDERED`, `broken image`;
3. `images.txt`: no `ERROR`; every `WARN` checked;
4. `provenance.txt`: OK;
5. the reviewer says SHIP and your spot checks agree.

## Orchestration (more than one deck)

- One **deck agent** per deck: it converts and later fixes (continue it by message, it keeps its context). Up to the number of agents the user allowed; start the next deck when one finishes.
- One **fresh reviewer** per deck and round.
- The **main agent** checks reference PDFs for all decks first (one question to the user), owns shared files (`style.css`, README, `public/shared/`, `vite.config.ts`, new slide classes — deck agents report what they need), does the spot checks, and keeps **`lessons.md`** in the run folder: every project-wide finding (a font problem, a class that does not work on two-cols, a parser trap) goes there at once and is sent to the running agents and given to every new one. In the WAST run this clearly lowered the error count of the later decks.
- No agent commits; the main agent commits per deck after the user agrees.

## Check mode (decks converted earlier)

For decks made before these checks existed: run Phase 1 for the .pptx, then add what the checks need — `ref:` markers for crop slides and pinned slides, `typo:` markers for typo fixes that were made silently (compare with the reference text), provenance comments and `PROVENANCE.md` rows — then run Phase 3. Without markers the lost-words count is not readable (hundreds of "missing" words).

## Phase 4: final report and handover

1. One last `compare.py` round.
2. Give the user the contact sheets (`sheet-NN.png`) and a short report: slide counts; deliberate differences (crops, formulas rewritten, layout changes); exceptions to the layout rules with reasons; what is open if the round limit was hit; whether the reference was a LibreOffice render; a section **"For you to decide"**: typo fixes (old → new), stale content kept verbatim (semesters, dates, break times), dropped visual elements, images that are not free.
3. Update the project settings section in the README.
4. Commit only after the user agrees.

## Files

- `scripts/extract.py` — PPTX → dump.md, slides.json, pictures.json, media/ (crops applied, covers, marks, click steps, embedded PDFs)
- `scripts/reference.py` — check and render the reference PDF; slide box
- `scripts/crop_ref.py` — crop a region of a reference page in slide % (footer corner white, near-white cleaned)
- `scripts/compare.py` — one check round
- `scripts/check_overflow.mjs` — overflow, clipped content, text under icons, broken images, sizes
- `scripts/check_images.py` — uncropped / rotated / stretched pictures, matched by content
- `scripts/provenance.py` — image provenance (follows `src:` imports)
- `scripts/lint_layout.py` — layout tricks, class on two-cols, YAML-tag layoutClass (run by compare.py)
- `scripts/deck.py` — deck parser and marker warnings (`python scripts/deck.py DECK.md`)
- `references/convert_brief.md`, `review_brief.md`, `fix_brief.md` — briefs for agents
- `references/pitfalls.md` — Slidev and PowerPoint traps from real runs
- `references/provenance.md` — provenance format and rules
