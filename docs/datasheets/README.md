# Datasheets and vendor documents

Every vendor document the design relies on is listed in
[`manifest.tsv`](manifest.tsv): datasheets, mechanical drawings, reference
designs and application notes. The PDFs themselves live in `files/`, which
git ignores. Vendors publish them under their own copyright and most state
no license to redistribute, so this public repo records where each one came
from and what it was, not the file.

## Getting the files

```sh
scripts/fetch-datasheets.sh
```

It downloads the rows marked `auto` and lists the rows marked `hand` with
the page to save them from. Some sites, LCSC among them, refuse scripted
downloads. Save those in a browser under the name in the `file` column.

## The manifest

One row per document, tab separated:

| Column | What it holds |
|--------|---------------|
| `file` | Name in `files/`: `<maker>-<part>.pdf`, lowercase. `-` for a web page with no PDF |
| `refs` | Schematic references that rely on it, such as `U2` or `SW1-SW12` |
| `part` | Maker and part number, plus what the document is |
| `kind` | `datasheet`, `drawing`, `reference`, `appnote` or `web` |
| `revision` | Revision and date printed on the document, once read |
| `get` | `auto` (the script fetches it), `hand` (saved in a browser) or `link` (read online) |
| `url` | Where it came from |
| `sha256` | Hash of the copy the design was checked against |

## Rules

- A value in a design doc that comes from a vendor document names it, with
  its revision, so a reader can find the same page.
- When a design check reads a document, fill in its `revision` and pin its
  `sha256`. The script prints the hash of an unpinned file.
- The script fails when a pinned file has changed. Read the new revision,
  recheck the values taken from it, then pin the new hash.
- A part's reasoning and the alternates it beat live in
  `docs/research/pcb-components/` and the change's `design.md`, not here.
