# Slidev pitfalls met in real conversions

Read this before converting. Each item cost a review round in an earlier run. Grouped by where it bites; the fix is after the arrow.

## Markdown and the parser (`mdc: true`, typographer)

- `[text]` in titles, text or R output (`[1] 0`) is eaten by MDC → `\[text\]`.
- `{ … }` is read as attributes; `A = { <img> }` can crash the slide → `\{ \}`.
- `--` becomes a dash, `+-` becomes `±` (typographer) → `&#45;&#45;`, `+&#45;`.
- `1)` at the start of a line becomes a list item → `1\)`; `* ` becomes a bullet → `\*`.
- `*…*` does not work inside raw HTML → `<em>`.
- `<` inside HTML blocks breaks the Vue build → `&lt;`.
- Blank lines inside a pre-like `<div>` turn the rest into a code block.
- A line directly after `---` is read as frontmatter if it looks like `key: value`; a comment like `<!-- typo: A -> B -->` there swallows slides → blank line first.
- The LAST comment of a slide is the speaker notes. Put markers and provenance at the top; a picture-only slide whose only comment is the provenance gets an empty `<!-- -->` at the end.
- Commas inside `layoutClass` values (`minmax(0,1fr)`) silently drop the last slides of the export.
- `layoutClass: !grid-cols-[…]` without quotes is a YAML tag: the value disappears → `layoutClass: '!grid-cols-[…]'`. Without `!` the layout's scoped CSS wins.

## Layouts

- `layout: two-cols` puts the title into the left column (it wraps) → almost always `two-cols-header`.
- `class:` on `two-cols` / `two-cols-header` lands on the column divs: exercise pencil, grey or code backgrounds vanish silently → put the class into `layoutClass`.
- `class:` on `layout: center` has no effect; `layoutClass` has no effect on default-layout slides.
- A too tall `two-cols-header` slide silently drops `::bottom::`, sometimes the whole left column. The overflow checker does not see it; the lost-words check does.
- A wide KaTeX `array`, a long code line or a long URL widens a grid column (min-content) and breaks the layout → split formulas, `[&_a]:break-all`.
- Default theme draws a grey line under every table row (on `tr`): layout tables need `[&_tr]:!border-0`.

## CSS and sizes

- The project base size is usually set in `style.css` (e.g. 1.3rem). "Bigger" from 1.1 to 1.3rem is hardly visible; `text-xl` (1.25rem) can be smaller than the base.
- `text-[…em]` inside `layoutClass`/`class:` refers to 16px, not to the slide base.
- Theme and project CSS beat utilities without `!`: `.slidev-layout p { margin }` beats `ml-8`, `img { object-fit: contain }` beats `object-fill`. Tables: `[&_thead_th]` works where `[&_th]` did not.
- `li` has line-height 1.8em, `p` a fixed `leading-6`: wrapped bullets look like two items. `leading-*` on a wrapper has no effect → `[&_li]:!leading-[1.45]` (or one project rule).
- `font-sans` in the default theme is Avenir Next, not the project font.
- Code size only via `[--slidev-code-font-size:…]`.
- Typographic quotes in `class=”…”` disable the class silently.
- Nothing below ~0.75em; do not let KaTeX break inside an expression.

## Formulas

- KaTeX does not render inside raw HTML (`<p>…$x$…</p>`); put math in Markdown paragraphs. KaTeX parse errors appear as raw text — look for `$` or `\` on the slide.
- `\operatorname{Var}` (else "V ar"). `\underset` labels are script-size and pull formulas apart → a separate text line below.
- If Slidev runs from a runtime outside the project, Vite may block the KaTeX fonts: formulas fall back to Times (sums and brackets too small) → `vite.config.ts` with `server.fs.allow` for the runtime. `compare.py` checks the fonts in the PDF.

## Pictures and PowerPoint features

- PowerPoint crops pictures (`srcRect`); the media file is uncropped. Raw files have shown private browser tabs, quiz answers and extra data → use the cropped file from `extract.py`; `check_images.py` finds raw ones.
- Shapes over pictures: white boxes that hide an answer until a click (`COVER`), circles/arrows that mark something (`MARK`) — both are in `dump.md`.
- Rotation and stretched frames are in `dump.md`; reproduce them.
- Click animations are in `dump.md` as `CLICK n:` lines. Without `v-click`, answers are visible at once. For click states inside a picture: render variants of the slide without the animated shapes (python-pptx: delete them, then LibreOffice), crop all variants identically, stack them (`<div class="grid [&>img]:[grid-area:1/1]">`) and reveal with `v-click`.
- Multi-step `<v-switch>` can render nothing in the plain export → check with `slidev export --with-clicks`.
- EMF/WMF with an embedded PDF (e.g. Beamer slides) render empty in LibreOffice → `extract.py` extracts the embedded PDF.

## Text

- Never add words, also not when a reviewer suggests it. Never complete text that is cut off in the original. Never "correct" German words on English slides (that is translation). Normalising "1,2,3.4" to "1, 2, 3.4" is a text change too.
- Never drop parts of a figure (axis titles, ticks) to solve an overlap.

## LibreOffice references

- Math text boxes (`mc:AlternateContent`) may be missing in the render: the `raw text:` line in `dump.md` is authoritative.
- Page numbers and an off-white background end up in crops → `crop_ref.py` paints the footer corner white and cleans near-white.
- Labels can wrap differently ("0.9 / 1") and formulas look rough; compare with the .pptx text.
- The slide sits at a different place on the page than in a PowerPoint PDF; `reference.json` has `slide_box_pt`.

## Shell

- zsh: `echo =====` fails (`=` expansion); word splitting of variables differs from bash.
