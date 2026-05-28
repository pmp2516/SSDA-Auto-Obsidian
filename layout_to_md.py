#!/usr/bin/env python3
"""
layout_to_md.py — Convert bounding-box layout JSON to Markdown.

Usage:
    python layout_to_md.py <filename> [--output path/to/out.md]

  <filename>  stem of the file pair, e.g. "mock" resolves to:
              outputs/mock-output-boxes.json   (layout input)
              data/mock.jpg  or  data/mock.png  (source image for cropping)

Output:
    outputs/{filename}.md
    outputs/{filename}-crops/crop_<n>.jpg   (one file per image/diagram region)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


OUTPUTS_DIR = Path("outputs")
DATA_DIR = Path("data")

# Fraction of the shorter box's height that must overlap to be considered
# on the same visual row.
_ROW_OVERLAP_THRESHOLD = 0.4

_DATE_RE = re.compile(r"^\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}$")
_PAGE_RE = re.compile(r"^p\.?\s*\d+$", re.IGNORECASE)


# ── reading order ──────────────────────────────────────────────────────────────

def _vertical_overlap_ratio(a: dict, b: dict) -> float:
    """Fractional vertical overlap relative to the shorter box's height."""
    _, ay, _, ah = a["bbox"]
    _, by, _, bh = b["bbox"]
    overlap = max(0, min(ay + ah, by + bh) - max(ay, by))
    shorter = min(ah, bh)
    return overlap / shorter if shorter > 0 else 0.0


def reading_order(boxes: list) -> list:
    """
    Group boxes into rows by vertical overlap, then order rows top-to-bottom
    and within each row left-to-right.
    """
    if not boxes:
        return []

    sorted_boxes = sorted(boxes, key=lambda b: b["bbox"][1])

    rows: list[list] = []
    for box in sorted_boxes:
        placed = False
        for row in rows:
            if any(_vertical_overlap_ratio(box, r) >= _ROW_OVERLAP_THRESHOLD for r in row):
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])

    ordered: list = []
    for row in sorted(rows, key=lambda r: min(b["bbox"][1] for b in r)):
        ordered.extend(sorted(row, key=lambda b: b["bbox"][0]))
    return ordered


# ── title detection ────────────────────────────────────────────────────────────

def _is_metadata(text: str) -> bool:
    """Return True for short strings that look like dates, page numbers, etc."""
    t = text.strip()
    return bool(_DATE_RE.match(t) or _PAGE_RE.match(t) or len(t) <= 10)


def _find_title_index(text_blocks: list) -> int:
    """
    Return the index (into text_blocks) of the first block that plausibly
    serves as the document title: single line, not metadata-like.
    """
    for i, text in enumerate(text_blocks):
        t = text.strip()
        if "\n" in t or _is_metadata(t):
            continue
        return i
    return -1


# ── source image lookup ────────────────────────────────────────────────────────

def _find_source_image(filename: str) -> Optional[Path]:
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        p = DATA_DIR / f"{filename}{ext}"
        if p.exists():
            return p
    return None


# ── OCR text → Markdown ────────────────────────────────────────────────────────

def _ocr_to_md(text: str) -> str:
    """Convert raw OCR text to Markdown, handling checkboxes and todo markers."""
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        # Unicode checked boxes
        if re.match(r"^[☑✓✔]\s*", s):
            s = "- [x] " + re.sub(r"^[☑✓✔]\s*", "", s)
        # Unicode unchecked boxes
        elif re.match(r"^[☐□]\s*", s):
            s = "- [ ] " + re.sub(r"^[☐□]\s*", "", s)
        # ASCII checked box anywhere in the line: [x] or [X]
        elif re.search(r"\[([xX])\]", s):
            s = "- [x] " + re.sub(r"\s*\[[xX]\]\s*", " ", s).strip()
        # ASCII unchecked box anywhere in the line: [ ]
        elif re.search(r"\[\s+\]", s):
            s = "- [ ] " + re.sub(r"\s*\[\s+\]\s*", " ", s).strip()
        lines.append(s)
    return "\n".join(lines)


# ── main conversion ────────────────────────────────────────────────────────────

def convert(filename: str) -> str:
    json_path = OUTPUTS_DIR / f"{filename}-output-boxes.json"
    if not json_path.exists():
        sys.exit(f"Error: {json_path} not found.")

    boxes: list = json.loads(json_path.read_text(encoding="utf-8"))
    ordered = reading_order(boxes)

    # Split into a flat item list preserving reading order.
    items: list[dict] = []
    for box in ordered:
        if box.get("type") == 1:
            raw = box.get("OCR", "").strip()
            if raw:
                items.append({"kind": "text", "text": raw})
        elif box.get("type") == 0:
            items.append({"kind": "image", "bbox": box["bbox"]})

    # Identify the title among all text blocks.
    text_blocks = [it["text"] for it in items if it["kind"] == "text"]
    title_idx = _find_title_index(text_blocks)

    # Prepare image cropping if there are image regions.
    image_items = [it for it in items if it["kind"] == "image"]
    crops_dir: Optional[Path] = None
    src_image: Optional[Path] = None

    if image_items:
        src_image = _find_source_image(filename)
        if src_image is None:
            print(
                f"Warning: no source image for '{filename}' in {DATA_DIR} — "
                "image regions will be noted as comments.",
                file=sys.stderr,
            )
        elif not PIL_AVAILABLE:
            print(
                "Warning: Pillow is not installed (pip install Pillow) — "
                "image regions will be noted as comments.",
                file=sys.stderr,
            )
        else:
            crops_dir = OUTPUTS_DIR / f"{filename}-crops"
            crops_dir.mkdir(parents=True, exist_ok=True)

    # Render Markdown blocks.
    md_blocks: list[str] = []
    text_counter = 0
    image_counter = 0

    for item in items:
        if item["kind"] == "text":
            text = item["text"]
            if text_counter == title_idx:
                md_blocks.append(f"# {text.strip()}")
            else:
                md_blocks.append(_ocr_to_md(text))
            text_counter += 1

        elif item["kind"] == "image":
            image_counter += 1
            label = f"image_{image_counter}"

            if crops_dir and src_image:
                crop_file = crops_dir / f"crop_{image_counter}.jpg"
                x, y, w, h = item["bbox"]
                pad = 100
                try:
                    with Image.open(src_image) as img:
                        iw, ih = img.size
                        x0 = max(0, x - pad)
                        y0 = max(0, y - pad)
                        x1 = min(iw, x + w + pad)
                        y1 = min(ih, y + h + pad)
                        img.crop((x0, y0, x1, y1)).save(crop_file)
                    # Path relative to the output .md (both live in outputs/)
                    rel = f"{filename}-crops/crop_{image_counter}.jpg"
                    md_blocks.append(f"![[{rel}]]")
                except Exception as exc:
                    print(f"Warning: could not crop {label}: {exc}", file=sys.stderr)
                    md_blocks.append(f"<!-- {label}: crop failed ({exc}) -->")
            else:
                md_blocks.append(f"<!-- {label}: image region bbox={item['bbox']} -->")

    return "\n\n".join(md_blocks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a layout bounding-box JSON to Markdown."
    )
    parser.add_argument(
        "filename",
        help="File stem, e.g. 'mock' reads outputs/mock-output-boxes.json",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path (default: outputs/{filename}.md)",
    )
    args = parser.parse_args()

    md = convert(args.filename)

    out_path = Path(args.output) if args.output else OUTPUTS_DIR / f"{args.filename}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
