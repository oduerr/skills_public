"""Read a Slidev deck into slides, in the order they are exported.

Used by compare.py and lint_layout.py. Handles headmatter, per-slide frontmatter,
`src:` imports of other files, fenced code blocks, and `hide: true` slides
(not exported, so not counted).

Marker comments the converter writes into a slide (read here):
  <!-- ref: p34 -->          this slide shows reference page 34
  <!-- ref: p34 crop -->     ... and is (mainly) a crop of that page, so its text is in the image
  <!-- typo: Celcius -> Celsius -->   a deliberate typo fix (the old word is not "lost")
  <!-- typo: "Insbesonder e" -> "Insbesondere" -->   quotes for more than one word
Put markers at the TOP of the slide: after the frontmatter, or after a blank line below
the `---` separator. At the end, Slidev shows them as speaker notes; directly after
`---`, Slidev reads them as YAML frontmatter and swallows slides. `python deck.py DECK.md`
warns about markers in both places.
"""
import re
from pathlib import Path

FENCE = re.compile(r"^\s*(```|~~~)")
YAML_LINE = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*:(.*)$")


def _split(lines):
    """Yield (frontmatter_lines, body_lines, start_line) per slide."""
    slides, i, n = [], 0, len(lines)
    fm, body, start = [], [], 1
    in_code = False

    def read_fm(k):
        """If lines[k:] start a frontmatter block that ends with '---', return (fm, next_k)."""
        j, block = k, []
        while j < n and lines[j].strip() != "---":
            block.append(lines[j])
            j += 1
        if j < n and block and all(YAML_LINE.match(l) or l.startswith((" ", "\t")) or not l.strip() for l in block) \
                and any(YAML_LINE.match(l) for l in block):
            return block, j + 1
        return None, k

    if n and lines[0].strip() == "---":
        f, k = read_fm(1)
        if f is not None:
            fm, i, start = f, k, k + 1
    while i < n:
        line = lines[i]
        if FENCE.match(line):
            in_code = not in_code
        if not in_code and line.rstrip() == "---":
            slides.append((fm, body, start))
            f, k = read_fm(i + 1)
            if f is not None:
                fm, body, start, i = f, [], k + 1, k
            else:
                fm, body, start, i = [], [], i + 2, i + 1
            continue
        body.append(line)
        i += 1
    slides.append((fm, body, start))
    return slides


def _fm_dict(fm):
    d = {}
    for l in fm:
        m = YAML_LINE.match(l)
        if m:
            d[m.group(1)] = m.group(2).strip().strip("'\"")
    return d


def read_deck(path, _depth=0):
    """Return a list of slides: {file, line, fm, body, hidden, pin, crop, typos, title}."""
    path = Path(path)
    out = []
    for fm, body, start in _split(path.read_text().splitlines()):
        d = _fm_dict(fm)
        text = "\n".join(body)
        if "src" in d and _depth < 5:
            sub = read_deck((path.parent / d["src"]).resolve(), _depth + 1)
            if sub and not text.strip():
                sub[0]["fm"] = {**sub[0]["fm"], **{k: v for k, v in d.items() if k != "src"}}
            out.extend(sub)
            continue
        if not text.strip() and not d:
            continue
        pin = re.search(r"<!--\s*ref:\s*p(\d+)(\s+crop)?\s*-->", text)
        title = next((re.sub(r"^#+\s*", "", l).strip() for l in body if re.match(r"^#\s", l)), "")
        out.append({
            "file": str(path), "line": start, "fm": d, "body": text,
            "hidden": d.get("hide", d.get("hidden", "")).lower() == "true",
            "pin": int(pin.group(1)) if pin else None, "crop": bool(pin and pin.group(2)),
            "typos": [(a or b, c or d) for a, b, c, d in re.findall(
                r'<!--\s*typo:\s*(?:"([^"]+)"|(\S+))\s*->\s*(?:"([^"]+)"|(\S+))\s*-->', text)],
            "title": title,
        })
    return out


def exported(path):
    """Slides that appear in an export (hidden ones removed), numbered from 1."""
    return [s for s in read_deck(path) if not s["hidden"]]


def marker_warnings(path, _depth=0):
    """Markers that Slidev would misread: on the first line after a '---' slide
    separator (read as YAML frontmatter), or at the very end of a slide (the
    comment at the end of a slide becomes the speaker notes)."""
    warn = []
    path = Path(path)
    for fm, body, start in _split(path.read_text().splitlines()):
        d = _fm_dict(fm)
        if "src" in d and _depth < 5:
            warn += marker_warnings((path.parent / d["src"]).resolve(), _depth + 1)
        if not fm and body and re.match(r"\s*<!--\s*(ref|typo):", body[0]):
            warn.append(f"{path.name}:{start}: marker directly after '---' (Slidev reads it as frontmatter); add a blank line before it")
        if re.search(r"<!--\s*(ref|typo):[^>]*-->\s*$", "\n".join(body)):
            warn.append(f"{path.name}:{start}: marker at the end of the slide (shown as speaker notes); move it to the top")
    return warn


if __name__ == "__main__":
    import sys
    for w in marker_warnings(sys.argv[1]):
        print("WARNING", w)
    for k, s in enumerate(exported(sys.argv[1]), 1):
        flags = (f" ref=p{s['pin']}" if s["pin"] else "") + (" crop" if s["crop"] else "")
        print(f"{k:3d} {Path(s['file']).name}:{s['line']} {s['title'][:60]}{flags}")
