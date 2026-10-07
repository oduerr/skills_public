"""Extract the visible slides of a .pptx into a text dump, a JSON index and a media folder.

Usage: python extract.py deck.pptx OUTDIR

Writes
  OUTDIR/dump.md      one block per visible slide: shapes with position (% of slide),
                      text, tables, images, notes, links, animations
  OUTDIR/slides.json  per visible slide: number, original number, title, all text
                      (full XML walk, used by compare.py for the lost-words check)
  OUTDIR/media/       images as sNN_<shape-id>.<ext> (NN = visible slide number)

Hidden slides are skipped, because PDF exports skip them too.
Text is also collected by walking the full slide XML (a:t and m:t, without
mc:Fallback), because python-pptx misses text inside mc:AlternateContent and
OMML math. If the "raw text" line of a slide has words that the shape list
does not show, look at the reference page: that text must not get lost.
Needs: python-pptx.
"""
import json
import os
import re
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"

src, out = sys.argv[1], sys.argv[2]
os.makedirs(f"{out}/media", exist_ok=True)
prs = Presentation(src)
W, H = prs.slide_width, prs.slide_height
lines = []


def pos(sh):
    try:
        return f"x={100*sh.left/W:.0f}% y={100*sh.top/H:.0f}% w={100*sh.width/W:.0f}% h={100*sh.height/H:.0f}%"
    except Exception:
        return "pos=?"


def omml_text(el):
    return "".join(t.text or "" for t in el.iter(f"{M}t"))


def raw_text(el):
    """All a:t and m:t text below el, skipping mc:Fallback (duplicate of the math)."""
    parts = []

    def walk(e):
        if e.tag == f"{MC}Fallback":
            return
        if e.tag in (f"{A}t", f"{M}t") and e.text:
            parts.append(e.text)
        for c in e:
            walk(c)

    walk(el)
    return " ".join(parts)


def para_text(p):
    parts = []
    for child in p._p:
        tag = child.tag
        if tag == f"{A}r":
            t = "".join(x.text or "" for x in child.iter(f"{A}t"))
            rpr = child.find(f"{A}rPr")
            if rpr is not None and rpr.get("b") == "1" and t.strip():
                t = f"**{t}**"
            parts.append(t)
        elif tag == f"{A}br":
            parts.append(" / ")
        elif tag == f"{A}fld":
            parts.append("".join(x.text or "" for x in child.iter(f"{A}t")))
        else:
            m = list(child.iter(f"{M}oMath"))
            if m:
                parts.append(" [MATH: " + " ".join(omml_text(x) for x in m) + "] ")
    return "".join(parts)


def dump_shape(sh, si, depth=0):
    ind = "  " * depth
    kind = sh.shape_type
    if kind == MSO_SHAPE_TYPE.GROUP:
        lines.append(f"{ind}- GROUP {pos(sh)}")
        for s in sh.shapes:
            dump_shape(s, si, depth + 1)
        return
    if kind == MSO_SHAPE_TYPE.PICTURE or hasattr(sh, "image"):
        try:
            img = sh.image
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", f"s{si:02d}_{sh.shape_id}.{img.ext}")
            with open(f"{out}/media/{name}", "wb") as f:
                f.write(img.blob)
            descr = sh._element.xpath(".//p:cNvPr/@descr")
            alt = f" descr='{descr[0]}'" if descr else ""
            lines.append(f"{ind}- IMAGE media/{name} {pos(sh)} ({img.size[0]}x{img.size[1]}px) name='{sh.name}'{alt}")
        except Exception as e:
            lines.append(f"{ind}- IMAGE? {sh.name} {pos(sh)} ({e}) -> crop from reference page")
        return
    if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
        txt = [(p.level, para_text(p)) for p in sh.text_frame.paragraphs]
        if not any(t.strip() for _, t in txt):
            m = list(sh._element.iter(f"{M}oMath"))
            if m:
                lines.append(f"{ind}- MATH {pos(sh)}: " + " | ".join(omml_text(x) for x in m))
            return
        ph = f" placeholder={sh.placeholder_format.type}" if sh.is_placeholder else ""
        lines.append(f"{ind}- TEXT {pos(sh)}{ph}")
        for lvl, t in txt:
            if t.strip():
                lines.append(f"{ind}    {'  '*lvl}* {t}")
        return
    if getattr(sh, "has_table", False) and sh.has_table:
        lines.append(f"{ind}- TABLE {pos(sh)}")
        for r in sh.table.rows:
            lines.append(f"{ind}    | " + " | ".join(c.text.replace(chr(10), ' ') for c in r.cells) + " |")
        return
    if getattr(sh, "has_chart", False) and sh.has_chart:
        lines.append(f"{ind}- CHART {pos(sh)} type={sh.chart.chart_type} -> crop from reference page")
        return
    xml = sh._element.xml
    if "videoFile" in xml or "audioFile" in xml or kind == MSO_SHAPE_TYPE.MEDIA:
        lines.append(f"{ind}- MEDIA/VIDEO {sh.name} {pos(sh)}")
        return
    m = list(sh._element.iter(f"{M}oMath"))
    if m:
        lines.append(f"{ind}- MATH {pos(sh)}: " + " | ".join(omml_text(x) for x in m))
        return
    if kind == MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT:
        lines.append(f"{ind}- OLE {sh.name} {pos(sh)} -> crop from reference page (formula? rewrite in KaTeX)")
        return
    lines.append(f"{ind}- SHAPE {kind} {sh.name} {pos(sh)}")


def title_of(slide):
    t = slide.shapes.title
    if t is not None and t.has_text_frame and t.text_frame.text.strip():
        return t.text_frame.text.strip().replace("\n", " ")
    return ""


index = []
vis = 0
masters = [m.part.partname for m in prs.slide_masters]
for i, slide in enumerate(prs.slides, 1):
    if slide._element.get("show") == "0":
        continue
    vis += 1
    title = title_of(slide)
    lines.append(f"\n## Slide {vis} (original #{i}) — title: {title or '(none)'}")
    mi = masters.index(slide.slide_layout.slide_master.part.partname)
    lines.append(f"layout: {slide.slide_layout.name} (master {mi})")
    for sh in slide.shapes:
        dump_shape(sh, vis)
    raw = raw_text(slide._element)
    lines.append("raw text: " + raw)
    rels = [r.target_ref for r in slide.part.rels.values() if r.is_external]
    if rels:
        lines.append("links: " + " ; ".join(rels))
    if "<p:timing" in slide._element.xml and "p:par" in slide._element.xml:
        lines.append("animations: yes (v-click only where it helps)")
    notes = ""
    if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if notes:
            lines.append("notes: " + notes.replace("\n", " / "))
    index.append({"slide": vis, "original": i, "title": title, "text": raw, "notes": notes})

with open(f"{out}/dump.md", "w") as f:
    f.write(f"# {os.path.basename(src)} — {vis} visible slides of {len(prs.slides)}, "
            f"size {W}x{H} EMU (ratio {W/H:.3f})\n" + "\n".join(lines) + "\n")
with open(f"{out}/slides.json", "w") as f:
    json.dump(index, f, ensure_ascii=False, indent=1)
print(f"{vis} visible slides ({len(prs.slides) - vis} hidden) -> {out}/dump.md, slides.json, media/")
