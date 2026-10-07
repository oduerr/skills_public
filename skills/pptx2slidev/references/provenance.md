# Image provenance

Lecture slides collect images from many places over the years: own plots, book covers, photos from the web, cartoons. When the deck becomes Markdown in a git repo, it is easy to publish it by mistake. So each image gets a record of where it came from and whether it may be published. Write this down during the conversion, because at that moment you see the original slide, its notes and its source line.

## Two places, same content

1. **Comment in the deck**, at the TOP of the slide (after the frontmatter, or after a blank line below `---`), so the author sees it while editing. Not at the end: Slidev shows the last comment of a slide as speaker notes (in one run 145 slides showed provenance in the presenter view). A picture-only slide ends with an empty `<!-- -->`.
   ```html
   <img src="/03_wkeit/elephant.jpg" class="h-72 mx-auto">
   <!-- provenance: elephant.jpg | 03_wkeit.pptx slide 11 (media s11_7.jpg) | Steve Jurvetson, "The elephant in the room", Wikimedia Commons | free | CC BY 2.0 -->
   ```
2. **Table** `PROVENANCE.md` in the image folder (`public/<deck>/PROVENANCE.md`, and `public/_intern/<deck>/PROVENANCE.md` for internal images), so scripts can read it (e.g. a public export that leaves out images that are not free):
   ```markdown
   | file | from | origin | rights | license | credit on slide |
   |---|---|---|---|---|---|
   | elephant.jpg | 03_wkeit.pptx slide 11 (media s11_7.jpg) | Steve Jurvetson, Wikimedia Commons, https://commons.wikimedia.org/... | free | CC BY 2.0 | yes |
   | ecdf.png | crop of reference page 14 | own R plot | own | – | – |
   | covers.png | 01_intro.pptx slide 12 | book covers (publishers) | unclear | – | – |
   ```

## Columns

- **file**: file name in the folder.
- **from**: where in the source it was taken: `<pptx> slide N (media <name>)`, or `crop of reference page N`.
- **origin**: who made it, where it comes from (author, URL, book, paper). Look in the slide's source line ("Quelle: …", "Source: …"), the speaker notes, the image's alt text / description (`descr=` in dump.md), and the file name. If nothing is known, write `unknown`.
- **rights**: exactly one of
  - `free` – a known free license or public domain (CC0, CC BY, CC BY-SA, public domain, official logos used as allowed),
  - `own` – made by the author (own plots, own diagrams, screenshots of own code),
  - `publisher` – from the author's own book or paper; the publisher holds the rights (not free);
  - `unclear` – everything else, including "found on the web" and book covers.
- **license**: e.g. `CC BY 2.0`, `CC0`, `public domain`, `–`.
- **credit on slide**: `yes` if the slide shows the attribution the license needs, else empty.

## Rules

- **Unclear and publisher count as not free.** Put such images into the internal folder of the deck (default `public/_intern/<deck>/`), which a public version leaves out. Do not guess a license to make an image "free".
- **Attribution:** a CC BY image needs a visible credit on the slide (author, title or source, license). Keep the original credit line or add one as the slide's single source line.
- **Crops** of the reference page inherit the rights of what is in them: a crop of an own diagram is `own`, a crop that contains a photo is that photo's rights.
- **Do not search the web** for licenses unless the user asks. Record what the slide and notes say, and list the unclear images in the final report so the author can decide.

Check with `python scripts/provenance.py DECK.md` before you report.
