# Brief: convert PowerPoint slides to Slidev

You convert one deck into a Slidev Markdown file. The author will teach from it: the content must stay exactly as it is, answers must stay hidden until the click that reveals them, and the slides must look like a clean version of the original.

Fill in before handing this to an agent: `<WORK>` (your own work folder), `<DECK_MD>`, `<IMG_DIR>` (`public/<deck>/`), `<INTERN_DIR>` (`public/_intern/<deck>/`), `<STYLE>` (theme, fonts, base size, slide classes, or "default theme, no custom CSS"), `<LANG>`, `<LESSONS>` (path of the run's lessons.md).

Read first: `references/pitfalls.md` and `<LESSONS>`.

## Inputs
- `<WORK>/dump.md`: per visible slide: shapes with position (% of slide), text, tables, pictures, and:
  - `raw text:` — all text in the slide XML, authoritative (formula text, math boxes);
  - `CROPPED … / ROTATED … / STRETCHED …` on pictures — `media/` files are already cropped; never use `*.raw.*` files (uncropped originals have shown private browser tabs, quiz answers, extra data);
  - `COVER` — a box over a picture or formula, often hiding an answer until a click;
  - `MARK` — a circle, frame or arrow drawn on a picture;
  - `CLICK n:` — what appears or disappears on each click;
  - `EMBEDDED PDF extracted` — use that PNG (LibreOffice renders these empty);
  - notes, links.
- `<WORK>/ref/p-NN.png` (low res) and `ref_hi/p-NN.png` (200 dpi): the reference pages. `reference.json` maps slides to pages (page ≠ slide: hidden slides are missing) and has `slide_box_pt`.
- `<WORK>/media/`: pictures (`sNN_<id>.<ext>`, NN = visible slide number).

## How to convert a slide
1. Read the slide block in dump.md AND look at the reference page.
2. Rebuild it: Markdown first, built-in layouts second, a little HTML last.
   - bullets → lists (keep levels); tables → Markdown tables; code → fenced blocks; links stay links; formulas → KaTeX (rewrite OLE/picture formulas from the reference page);
   - side by side → `two-cols-header` (title above, `::left::`, `::right::`, `::bottom::`), `image-left` / `image-right` (`backgroundSize: contain`), `image`, `section`, `cover`; left-to-right sequences → a Markdown table or a one-row HTML table with `[&_tr]:!border-0`;
   - pictures: `<img src="/<deck>/x.png" class="h-72 mx-auto">` — always a height or `max-h-[..]`; reproduce rotation (`rotate-90`) and stretching (fixed box + `!object-fill`).
3. **Click steps** (`CLICK n:` lines): reproduce every one with `v-click` / `<v-clicks>` / `v-after` / `v-switch`. A shape that appears on a click is hidden until then; a COVER that disappears on a click hides what is under it until then. If the click changes something inside a picture (annotations on a plot, a cover over part of a screenshot): render variants of the slide without the animated shapes (python-pptx: delete them, save, render with LibreOffice), crop all variants identically with `scripts/crop_ref.py`, stack them (`<div class="grid [&>img]:[grid-area:1/1]">`) and reveal with `v-click`. Multi-step `v-switch` may render nothing in the plain export: check with `--with-clicks`.
4. **COVER without click**: reproduce it (the original hides something on purpose). **MARK**: reproduce it — crop the region from the reference page if it cannot be rebuilt.
5. **No absolute positioning** (`absolute`, offsets, fixed px boxes, inline `style=` positions), except one source or credit line per slide. Why: absolute boxes do not move with the content; when text or fonts change they drift over other content. If a slide really needs it, do it and list it.
6. **No custom grid divs or new CSS classes** unless `<STYLE>` provides them. Slide classes (exercise, code, blackboard) on `two-cols*` slides go into `layoutClass:` (quoted when it starts with `!`), not `class:`.
7. Not usable as an image file (WMF/EMF without embedded PDF, charts, SmartArt, rotated text, arrows over pictures): crop from the reference page with `scripts/crop_ref.py <WORK> <page> <x> <y> <w> <h> out.png` (slide %, from dump.md). It paints the page-number corner white instead of cutting it away and cleans an off-white background. Check the crop edges. A slide that is mostly graphics may be cropped whole below the title; prefer real text where reasonable.
8. Copy only the pictures you use into `<IMG_DIR>`. Provenance for each (comment at the TOP of the slide AND a row in `<IMG_DIR>/PROVENANCE.md`), see `references/provenance.md`. Not free (`unclear`, `publisher`) → `<INTERN_DIR>`, row in its PROVENANCE.md.
9. Speaker notes: verbatim, as the LAST comment of the slide. A slide without notes whose last comment would be a marker or provenance gets an empty `<!-- -->` at the end.
10. **Visual signals** that recur (exercise pencil, blackboard, code background) → the project's slide classes. If a class is missing, report it to the main agent; do not drop the signal.
11. **Break slides** (title with "Pause"/"Break"): title and text verbatim, including times and semesters; no layout work.
12. **Markers** for the check scripts, at the TOP of the slide (after the frontmatter, or after a BLANK line below `---`):
    - `<!-- ref: pNN -->` slide differs a lot from its page (e.g. rebuilt as a table);
    - `<!-- ref: pNN crop -->` slide is mainly a crop of page NN; `<!-- ref: pNN partial -->` part of it is;
    - `<!-- ref: none -->` a slide without reference page;
    - `<!-- typo: old -> new -->` per typo fix; quotes for several words.
13. Skip slide-number boxes and footer boilerplate. Videos: placeholder `*(Video: <name>)*` unless told otherwise.

## Text: the hard rules
- Never shorten, summarise, paraphrase, translate or "improve" text; never add words (also not when a reviewer suggests it); never complete text that is cut off in the original; never "correct" words of another language (German on an English slide). Fix only obvious typos, each with a `typo:` marker. Why: these are the author's teaching words; every change is something the author has to find and undo.
- Never drop parts of a figure (axis titles, ticks, labels) to solve an overlap.

## Before you report
- `$PY <SKILL>/scripts/compare.py <DECK_MD> <WORK> <WORK>/round-00`, `node <SKILL>/scripts/check_overflow.mjs <DECK_MD>`, `$PY <SKILL>/scripts/check_images.py <DECK_MD> <WORK>`, `$PY <SKILL>/scripts/provenance.py <DECK_MD>`. Fix clear problems once; a check loop follows.
- Look yourself at every slide with CLICK, COVER, CROPPED or a crop from the reference, in its final and its first click state.
- Report: file, slide count, slides with crops, click steps reproduced (and how), exceptions to the layout rules with reasons, typo fixes (old → new), stale content kept verbatim, visual elements dropped, pictures that are not free, open problems. Report only what you checked.
