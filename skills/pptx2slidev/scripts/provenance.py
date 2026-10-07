"""Check the provenance of every image a Slidev deck uses.

Usage: python provenance.py DECK.md [--public-dir DIR] [--intern-dir _intern]

Every image file referenced by the deck, also in files imported with `src:`
(<img src>, ![](...), image:/background: frontmatter, url(...)), must have
  1. a row in PROVENANCE.md in the same folder as the image (e.g. public/<deck>/PROVENANCE.md)
  2. a provenance comment on the slide: <!-- provenance: <file> | ... -->
     (at the TOP of the slide: a comment at the end becomes the speaker notes)

The public folder is found next to the deck or in a parent folder (the Slidev
project root); --public-dir overrides it.

Table format (see references/provenance.md):
| file | from | origin | rights | license | credit on slide |

rights is one of: free, own, publisher, unclear.
  publisher = from the author's own book or paper, the publisher holds the rights
Problems reported:
  - image without table row or without comment
  - an image folder without PROVENANCE.md (loud: nothing in it is documented)
  - rights other than free/own for a file outside the internal folder
    (--intern-dir, default _intern; _intern/<deck>/ counts as inside):
    unclear and publisher count as NOT free, so they must not go into a public version
  - license that needs attribution (CC BY*) with an empty "credit on slide"
Exit code 1 if there are problems.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck import read_deck  # noqa: E402

args = sys.argv[1:]
deck = Path(args[0]).resolve()
intern = args[args.index("--intern-dir") + 1] if "--intern-dir" in args else "_intern"
if "--public-dir" in args:
    public = (deck.parent / args[args.index("--public-dir") + 1]).resolve()
else:
    public = next((d / "public" for d in [deck.parent, *deck.parents] if (d / "public").is_dir()), deck.parent / "public")

slides = read_deck(deck)
text = "\n".join(s["body"] + "\n" + "\n".join(f"{k}: {v}" for k, v in s["fm"].items()) for s in slides)

refs = set()
for pat in [r'<img[^>]+src="([^"]+)"', r"!\[[^\]]*\]\(([^)\s]+)", r"^(?:image|background):\s*['\"]?([^'\"\s]+)",
            r"url\(['\"]?([^'\")#]+)"]:
    refs.update(re.findall(pat, text, flags=re.M))
refs = {r for r in refs if not r.startswith(("http://", "https://", "data:", "#")) and re.search(r"\.\w{2,4}$", r)}

comments = set(re.findall(r"<!--\s*provenance:\s*([^|\s]+)", text))

folders = {(public / r.lstrip("/")).resolve().parent for r in refs}
tables, missing_tables = {}, []
for folder in sorted(folders):
    f = folder / "PROVENANCE.md"
    if not f.exists():
        missing_tables.append(folder)
        continue
    for line in f.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0] not in ("file", "") and not set(cells[0]) <= set("-: "):
            tables[str((folder / cells[0].strip("`")).resolve())] = dict(zip(["file", "from", "origin", "rights", "license", "credit"], cells[:6]))

problems, unclear = [], []
for folder in missing_tables:
    rel = folder.relative_to(public.parent) if folder.is_relative_to(public.parent) else folder
    problems.append(f"NO PROVENANCE.md in {rel}/ — none of its images are documented")
for r in sorted(refs):
    path = (public / r.lstrip("/")).resolve()
    name = os.path.basename(r)
    row = tables.get(str(path))
    if row is None and path.parent not in missing_tables:
        problems.append(f"{r}: no row in PROVENANCE.md of its folder")
    if name not in comments and r not in comments and r.lstrip("/") not in comments:
        problems.append(f"{r}: no <!-- provenance: {name} | ... --> comment in the deck")
    if row:
        rights = row["rights"].lower()
        in_intern = f"/{intern}/" in str(path)
        if rights not in ("free", "own"):
            unclear.append(f"{r} [{rights or 'missing'}] ({row['origin'] or 'origin unknown'})")
            if not in_intern:
                problems.append(f"{r}: rights '{row['rights'] or 'missing'}' but not in {intern}/ (only free/own may be outside)")
        if re.search(r"CC[- ]?BY", row["license"], re.I) and not row["credit"]:
            problems.append(f"{r}: {row['license']} needs a credit on the slide")

print(f"{len(refs)} images referenced in {len(slides)} slides, {len(folders)} image folders, "
      f"{len(tables)} table rows for them, {len(comments)} comments")
if unclear:
    print(f"\nNot free ({len(unclear)}), the author decides:")
    for u in unclear:
        print("  -", u)
if problems:
    print(f"\nProblems ({len(problems)}):")
    for p in problems[:80]:
        print("  -", p)
    if len(problems) > 80:
        print(f"  ... {len(problems) - 80} more")
    sys.exit(1)
print("provenance OK")
