# Brief: convert PowerPoint slides to Slidev

You convert one deck (or a given slide range) into a Slidev Markdown file. The author will teach from it, so the content must stay exactly as it is, and the slides must look like a clean version of the original.

Fill in before handing this to an agent: `<WORK>` (work folder), `<DECK_MD>` (target file), `<IMG_DIR>` (e.g. `public/<deck>/`), `<INTERN_DIR>` (e.g. `public/_intern/<deck>/`), `<STYLE>` (what the project's style decisions are: theme, fonts, base size, existing CSS helpers or "default theme, no custom CSS"), `<LANG>`.

## Inputs
- `<WORK>/dump.md`: per visible slide: shapes with position (% of slide), text, tables, images, notes, links, animations, and a `raw text:` line with all text in the slide XML.
- `<WORK>/media/`: the images (`sNN_<id>.<ext>`, NN = visible slide number).
- `<WORK>/ref/p-NN.png`: the reference page (low resolution) — LOOK at it for every slide; it shows the real layout. `<WORK>/ref_hi/p-NN.png`: 200 dpi, for crops. `<WORK>/reference.json` maps slide numbers to page numbers (hidden slides are missing in the PDF, so page ≠ slide).

## How to convert a slide
1. Read the slide block in dump.md AND look at the reference page.
2. Compare the `raw text:` line with the shape list. Words that appear only in the raw text (text in math or special objects) still belong on the slide.
3. Rebuild it with Markdown first, built-in layouts second, a little HTML last:
   - bullets → Markdown lists (keep levels); tables → Markdown tables; R/Python code → fenced code blocks; links stay links; formulas → KaTeX `$…$` / `$$…$$` (rewrite OLE / image formulas from the reference page).
   - side by side → built-in layouts: `two-cols` / `two-cols-header` (has a `::bottom::` slot), `image-left` / `image-right` (with `backgroundSize: contain`), `image` for a full-slide picture, `section`, `cover`. For a left-to-right sequence (timeline, prompt → result) use a Markdown table or a one-row HTML table.
   - images: `<img src="/<deck>/x.png" class="h-72 mx-auto">` — always give a height (`h-60` … `h-96`) or `max-h-[..]`.
4. **No absolute positioning** (`absolute`, `top-[..]`, `left-[..]`, fixed px boxes), except one source or credit line per slide. Why: absolute boxes do not move with the content; when text or fonts change, they drift over other content, and every later fix gets harder. If you think a slide really needs it, do it and list it in your report.
5. **No custom grid divs or new CSS classes** unless `<STYLE>` provides them. Built-in layouts are understood by every later editor and agent.
6. Things that are not usable as an image file (WMF/EMF, charts, SmartArt, arrows or labels over pictures, rotated text): crop the region from `ref_hi/p-NN.png` with Pillow, using the % position from dump.md. Check the crop edges (do not cut a text line in half). RGBA/TIFF: composite onto white before saving as PNG. If a slide is mostly graphics, cropping the whole content area below the title is fine; prefer real text where it is reasonable.
7. Copy only the images you use into `<IMG_DIR>`. For each image add provenance (comment next to it AND a row in `<IMG_DIR>/PROVENANCE.md`) following `references/provenance.md`. Images with rights `unclear` go to `<INTERN_DIR>`, with their row in `<INTERN_DIR>/PROVENANCE.md`.
8. Animations: `v-click` only where it clearly helps (quiz answers, step-by-step reveals).
9. Speaker notes: keep them verbatim as an HTML comment at the end of the slide.
10. **Visual signals** that recur across slides (a pencil on exercise slides, a blackboard background or a small blackboard icon for "go to the board", a code-style background) carry meaning for the teacher. Map them to the project's slide classes from `<STYLE>`. If the project has no class for a recurring signal, do not drop it silently: report it, and propose a class (CSS only if possible, so there is no image-rights question).
11. **Break slides** (title "Pause …"): take over title and text verbatim, including times and semesters. No layout work, no reference page needed.
12. **Markers** (read by the check scripts, invisible on the slide). Put them at the TOP of the slide: after the closing `---` of the slide's frontmatter, or, on a slide without frontmatter, after a BLANK line below the `---` separator. Two traps: at the end of a slide, Slidev shows the last comment as speaker notes; directly on the line after `---`, Slidev reads `<!-- typo: A -> B -->` as YAML frontmatter and swallows whole slides.
   - `<!-- ref: pNN -->` when a slide's text differs a lot from its reference page (e.g. rebuilt as a table), so the comparison pairs it correctly;
   - `<!-- ref: pNN crop -->` when the slide is mainly a crop of reference page NN (its words are in the image);
   - `<!-- typo: old -> new -->` for every typo you fix, one per fix; use quotes for more than one word: `<!-- typo: "Insbesonder e" -> "Insbesondere" -->`.
13. Skip slide-number boxes and footer boilerplate. Videos: placeholder line `*(Video: <name>)*` unless told otherwise.

## Text: the hard rule
Never shorten, summarise, paraphrase, translate or "improve" text. Every word stays. Fix only obvious typos, mark each with a `<!-- typo: old -> new -->` comment, and list them. Why: these are the author's teaching words; a shortened sentence is a content change the author has to find and undo.

## KaTeX pitfall
KaTeX does not render inside raw HTML like `<p>…$x$…</p>`. Put math in Markdown paragraphs (inside a `<div>`, leave blank lines around the Markdown).

## Before you report
- Run `node <SKILL>/scripts/check_overflow.mjs <DECK_MD>` once and fix clear overflow. A layout loop follows, so do not spend more than one fix round.
- Run `python <SKILL>/scripts/provenance.py <DECK_MD>` and `python <SKILL>/scripts/lint_layout.py <DECK_MD>`; fix flags or give the reason.
- Report: file written, number of slides, slides with crops, exceptions to the layout rules (with reasons), typos fixed (old → new), stale content you kept verbatim (old dates, semesters, calendars), visual elements you dropped, images with unclear rights, open problems.
