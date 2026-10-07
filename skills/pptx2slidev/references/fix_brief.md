# Brief: fix one round

You fix the problems a reviewer listed in one Slidev file. You do not change wording.

Fill in: `<DECK_MD>`, `<ROUND_DIR>`, `<LIST>` (the reviewer's MUST and SHOULD items for your pages), `<STYLE>`.

## How
1. Read the file. For each item, look at `<ROUND_DIR>/cmp-NN.png` to see the problem yourself.
2. Fix in this order: lost text, overflow and broken images, unreadable content, then size and balance.
3. Ways to make things fit, best first: smaller image height; two columns (built-in layout); a wrapper with a slightly smaller em-based font size for that slide. Ways to fill an empty slide: bigger images, bigger text. Not: spacing hacks (`mt-12`, `space-y-8`, `h-full justify-center`) — they push titles around and break on the next change.
4. Utility classes that lose against Slidev's base CSS (tables, blockquotes) need the `!` prefix (`!py-1`, `!text-[1.1em]`). `text-xl` is 20 px, smaller than the ~21 px base, so it does not make text bigger.
5. Use straight quotes in HTML attributes (`class="…"`). Typographic quotes make the class silently fail.

## Hard rules
- Never shorten, paraphrase or remove text. If it does not fit, change size or layout.
- No absolute positioning except one source/credit line per slide. No new custom CSS unless `<STYLE>` allows it.
- Do not touch slides that are not in your list, files other than `<DECK_MD>`, or the project's CSS/layouts.
- Keep speaker notes and provenance comments.

## Verify your own work
Run `node <SKILL>/scripts/check_overflow.mjs <DECK_MD>` and `python <SKILL>/scripts/lint_layout.py <DECK_MD>` and read the lines for your pages. Any layout flag you added must be removed or reported as an exception with its reason — an unreported flag counts as a false report. Every overflow on your pages must be gone (at most 3 runs). Do not claim a fix you did not check.

## Report
One line per item: `page NN: fixed – <what you changed>` or `page NN: not fixed – <why>`.
