from datetime import datetime
import re
from dataclasses import asdict
import click
from pathlib import Path
from search import RetrievalSystem

from llm import LLMClient, VLLMClient


@click.group()
def cli():
    """Auto-Obsidian: OCR-to-vault pipeline."""
    pass


@cli.command("add-note")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True), help="Path to the input image.")
@click.option("--vault", required=True, type=click.Path(), help="Path to the Obsidian vault.")
@click.option("--index-path", required=True, type=click.Path(), help="Path to the index.")
def add_note(input_path: str, vault: str, index: str):
    """Process a handwritten image and write a new note into the vault."""
    image_path = Path(input_path)
    vault_path = Path(vault)
    index_path = Path(index)
    click.echo(f"Loading or building index at {index_path}")
    retrieval = _rebuild_index(vault_path, index_path)

    click.echo(f"Processing image: {image_path}")

    extracted = _run_ocr(image_path)
    click.echo("OCR complete.")

    template = _retrieve_template(extracted, retrieval)
    click.echo(f"Matched template: {template['name']}")

    link_candidates = _retrieve_candidates(extracted, retrieval)

    note_content = _render_note(extracted, template, link_candidates, client=LLMClient())

    _write_note(note_content, vault_path)
    click.echo(f"Note written to vault: {vault_path}")


@cli.command("fill-template")
@click.option("--text", required=True, help="Extracted text to fill into the template.")
@click.option("--template", "template_path", required=True, type=click.Path(exists=True), help="Path to the markdown template file.")
def fill_template(text: str, template_path: str):
    """Fill a markdown template with the given text using the LLM."""
    template_content = Path(template_path).read_text()
    result = LLMClient().fill_template(text, template_content)
    click.echo(result)


@cli.command("update-index")
@click.option("--vault", required=True, type=click.Path(exists=True), help="Path to the Obsidian vault.")
@click.option("--index-path", required=True, type=click.Path(), help="Path to the index.")
def update_index(vault: str, index: str):
    """Scan the vault and rebuild the index."""
    vault_path = Path(vault)
    index_path = Path(index)
    click.echo(f"Scanning vault: {vault_path}")
    _rebuild_index(vault_path, index_path)
    click.echo("Index updated.")



def _run_ocr(image_path: Path) -> dict:
    """Call the OCR service and return structured extraction results.

    Returns a dict with keys:
        bbox  (list[int]) - list of 4 ints [x0, y0, w, h] corresponding to top left corner of text or image bounding box and width and height of the bounding box
        ocr   (str) - cleaned full text contained within the region reported in "bbox", empty string if the region contains no text
        type  (int) - 1 if region only contains text, 0 if the region contains a scribble, image, plot, etc.
    """
    return VLLMClient().extract_ocr(image_path)


def _retrieve_template(extracted: dict, retrieval: RetrievalSystem) -> dict:
    """Query for the best-matching note template.

    Args:
        extracted: output of _run_ocr

    Returns a dict with at least:
        name     (str) — template identifier
        content  (str) — raw template markdown
    """
    return asdict(retrieval.retrieve_template(extracted['OCR']))

def _retrieve_candidates(extracted: dict, retrieval: RetrievalSystem) -> list[tuple[int, int, list[dict]]]:
    spans = [
        (
            matches[i].start(),
            matches[i + n - 1].end(),
            extracted["OCR"][matches[i].start():matches[i + n - 1].end()],
        )
        for matches in [list(re.finditer(r"\w+", extracted["OCR"]))]
        for n in (1, 2, 3)
        for i in range(len(matches) - n + 1)
    ]
    return retrieval.propose_links(spans)


def _render_note(extracted: dict, template: dict, link_candidates: list, client: LLMClient) -> str:
    """Merge OCR output into the template to produce the final note markdown.

    Args:
        extracted: output of _run_ocr — expects keys: text, todos, tags
        template:  output of _retrieve_template — expects key: content
        client:    shared LLMClient instance

    Returns the complete note as a markdown string.
    """
    extracted_text = extracted.get("text", "")
    if extracted.get("todos"):
        extracted_text += "\n\nTodos:\n" + "\n".join(f"- {t}" for t in extracted["todos"])

    return client.fill_template(extracted_text, template["content"])


def _parse_tags(content: str) -> list[str]:
    """Extract tags from YAML front-matter and inline #tag syntax."""
    tags: list[str] = []

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        # tags: [a, b, c]  or  tags: a, b
        inline = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.MULTILINE)
        if inline:
            tags += [t.strip().lstrip("#") for t in inline.group(1).split(",") if t.strip()]
        else:
            # tags:\n  - a\n  - b
            block = re.search(r"^tags:\s*\n((?:[ \t]+-[^\n]*\n?)+)", fm, re.MULTILINE)
            if block:
                tags += [re.sub(r"^[ \t]+-\s*", "", l).strip().lstrip("#")
                         for l in block.group(1).splitlines() if l.strip()]
            else:
                # tags: a, b
                flat = re.search(r"^tags:\s*(.+)", fm, re.MULTILINE)
                if flat:
                    tags += [t.strip().lstrip("#") for t in flat.group(1).split(",") if t.strip()]

    body = content[fm_match.end():] if fm_match else content
    tags += [m.group(1) for m in re.finditer(r"(?<!\w)#([\w/-]+)", body)]

    return [t.lower() for t in tags if t]


def _build_folder_histograms(vault_path: Path) -> dict[Path, dict[str, int]]:
    """For each top-level folder in the vault build a {tag: count} histogram."""
    histograms: dict[Path, dict[str, int]] = {}
    for folder in sorted(vault_path.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        counts: dict[str, int] = {}
        for md_file in folder.rglob("*.md"):
            try:
                file_tags = _parse_tags(md_file.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
            for tag in file_tags:
                counts[tag] = counts.get(tag, 0) + 1
        histograms[folder] = counts
    return histograms


def _pick_folder(note_tags: list[str], histograms: dict[Path, dict[str, int]], vault_path: Path) -> Path:
    """Return the top-level folder whose tag histogram best matches note_tags."""
    if not note_tags or not histograms:
        return vault_path

    best_folder = vault_path
    best_score = -1
    for folder, counts in histograms.items():
        score = sum(counts.get(tag, 0) for tag in note_tags)
        if score > best_score:
            best_score = score
            best_folder = folder

    # Fall back to vault root when no folder has any matching tag
    return best_folder if best_score > 0 else vault_path


def _write_note(content: str, vault_path: Path) -> None:
    """Write the rendered note into the vault.

    Picks the best top-level folder via tag-histogram matching, then writes
    a timestamped .md file there.
    """
    note_tags = _parse_tags(content)
    histograms = _build_folder_histograms(vault_path)
    target_folder = _pick_folder(note_tags, histograms, vault_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"note_{timestamp}.md"
    target_path = target_folder / filename
    target_path.write_text(content)
    click.echo(f"Note written to: {target_path} (tags matched: {note_tags})")


def _rebuild_index(vault_path: Path, index_path: Path) -> RetrievalSystem:
    # TODO: walk vault_path for *.md files, embed each with a chosen model,
    #       upsert into a Qdrant collection keyed by file path hash
    templates = []
    docs = []
    return RetrievalSystem.build(templates, docs, index_dir=index_path)


if __name__ == "__main__":
    cli()
