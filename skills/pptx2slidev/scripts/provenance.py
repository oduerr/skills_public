"""Check the provenance of every image a Slidev deck uses.

Usage: python provenance.py DECK.md [--public-dir public] [--intern-dir _intern]

Every image file referenced by the deck (<img src>, ![](...), image:/background:
frontmatter, url(...)) must have
  1. a row in PROVENANCE.md in the same folder as the image (e.g. public/<deck>/PROVENANCE.md)
  2. a provenance comment next to it in the deck: <!-- provenance: <file> | ... -->

Table format (see references/provenance.md):
| file | from | origin | rights | license | credit on slide |

rights is one of: free, own, unclear.
Problems reported:
  - image without table row or without comment
  - rights "unclear" (or missing) for a file outside the internal folder (--intern-dir,
    default _intern; subfolders per deck such as _intern/<deck>/ count as inside):
    unclear counts as NOT free, so it must not go into a public version
  - license that needs attribution (CC BY*) with an empty "credit on slide"
Exit code 1 if there are problems.
"""
import os
import re
import sys
from pathlib import Path

args = sys.argv[1:]
deck = Path(args[0]).resolve()
public = deck.parent / (args[args.index("--public-dir") + 1] if "--public-dir" in args else "public")
intern = args[args.index("--intern-dir") + 1] if "--intern-dir" in args else "_intern"
text = deck.read_text()

refs = set()
for pat in [r'<img[^>]+src="([^"]+)"', r"!\[[^\]]*\]\(([^)\s]+)", r"^(?:image|background):\s*['\"]?([^'\"\s]+)",
            r"url\(['\"]?([^'\")]+)"]:
    refs.update(re.findall(pat, text, flags=re.M))
refs = {r for r in refs if not r.startswith(("http://", "https://", "data:"))}

comments = set(re.findall(r"<!--\s*provenance:\s*([^|\s]+)", text))

tables = {}
for f in public.rglob("PROVENANCE.md"):
    for line in f.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0] not in ("file", "") and not set(cells[0]) <= set("-: "):
            key = str((f.parent / cells[0].strip("`")).resolve())
            tables[key] = dict(zip(["file", "from", "origin", "rights", "license", "credit"], cells[:6]))

problems, unclear = [], []
for r in sorted(refs):
    path = (public / r.lstrip("/")).resolve()
    name = os.path.basename(r)
    row = tables.get(str(path))
    if row is None:
        problems.append(f"{r}: no row in {path.parent.relative_to(deck.parent) if path.parent.is_relative_to(deck.parent) else path.parent}/PROVENANCE.md")
    if name not in comments and r not in comments and r.lstrip("/") not in comments:
        problems.append(f"{r}: no <!-- provenance: {name} | ... --> comment in the deck")
    if row:
        rights = row["rights"].lower()
        in_intern = f"/{intern}/" in str(path)
        if rights not in ("free", "own"):
            unclear.append(f"{r} ({row['origin'] or 'origin unknown'})")
            if not in_intern:
                problems.append(f"{r}: rights '{row['rights'] or 'missing'}' but not in {intern}/ (unclear counts as not free)")
        if re.search(r"CC[- ]?BY", row["license"], re.I) and not row["credit"]:
            problems.append(f"{r}: {row['license']} needs a credit on the slide")

print(f"{len(refs)} images referenced, {len(tables)} table rows, {len(comments)} comments")
if unclear:
    print(f"\nRights unclear ({len(unclear)}), ask the author:")
    for u in unclear:
        print("  -", u)
if problems:
    print(f"\nProblems ({len(problems)}):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("provenance OK")
