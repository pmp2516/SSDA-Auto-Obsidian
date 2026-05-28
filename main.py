import re
from dataclasses import asdict
import click
from pathlib import Path
from search import RetrievalSystem
from chunk import get_all_notes, get_all_templates


@click.group()
def cli():
    """Auto-Obsidian: OCR-to-vault pipeline."""
    pass


@cli.command("add-note")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True), help="Path to the input image.")
@click.option("--vault", required=True, type=click.Path(), help="Path to the Obsidian vault.")
@click.option("--index-path", "index", required=True, type=click.Path(), help="Path to the index.")
def add_note(input_path: str, vault: str, index: str):
    """Process a handwritten image and write a new note into the vault."""
    image_path = Path(input_path)
    vault_path = Path(vault)
    index_path = Path(index)
    click.echo(f"Loading or building index at {index_path}")
    retrieval = _rebuild_index(vault_path, index_path)

    click.echo(f"Processing image: {image_path}")

    extracted = _run_ocr(image_path)
    # extracted = { "OCR": "The quick brown fox jumps over the lazy dog." }
    click.echo("OCR complete.")

    template = _retrieve_template(extracted, retrieval)
    click.echo(f"Matched template: {template['path']}")

    link_candidates = _retrieve_candidates(extracted, retrieval)

    note_content = _render_note(extracted, template, link_candidates)

    _write_note(note_content, vault_path)
    click.echo(f"Note written to vault: {vault_path}")


@cli.command("update-index")
@click.option("--vault", required=True, type=click.Path(exists=True), help="Path to the Obsidian vault.")
@click.option("--index-path", "index", required=True, type=click.Path(), help="Path to the index.")
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
        text       (str)  — full transcribed text
        todos      (list) — extracted to-do items
        scribbles  (list) — extracted scribble regions
        tags       (list) — inferred tags / keywords for template matching
    """
    # TODO: integrate OCR service (e.g. Google Vision, Tesseract, or custom model)
    raise NotImplementedError("OCR service not yet implemented")


def _retrieve_template(extracted: dict, retrieval: RetrievalSystem) -> dict:
    """Query for the best-matching note template.

    Args:
        extracted: output of _run_ocr

    Returns a dict with at least:
        id       (str) — template identifier
        content  (str) — raw template markdown
        path     (Path) — path to the template
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


def _render_note(extracted: dict, template: dict, link_candidates: list) -> str:
    """Merge OCR output into the template to produce the final note markdown.

    Args:
        extracted: output of _run_ocr
        template:  output of _retrieve_template

    Returns the complete note as a markdown string.
    """
    # import json
    # print(json.dumps(
    #     {"extracted": extracted, "template": template, "link_candidates": link_candidates},
    #                  indent=2, default=str))
    # TODO: use a templating engine (e.g. Jinja2) or simple string substitution
    #       or even some small model prompting to merge extracted text into the template content,
    #       to fill in {{text}}, {{todos}}, {{date}}, etc.
    raise NotImplementedError("Note rendering not yet implemented")


def _write_note(content: str, vault_path: Path) -> None:
    """Write the rendered note into the vault.

    Determines the target sub-folder and file name from the note front-matter
    or a configured naming convention, then writes the .md file.
    """
    # TODO: parse front-matter for folder/title, handle filename collisions,
    #       optionally trigger an Obsidian URI to open the new note

    # We can also use the Obsidian MCP here to trigger a sync, but for now better
    # keep it simple and just write the file 
    raise NotImplementedError("Vault writer not yet implemented")


def _rebuild_index(vault_path: Path, index_path: Path) -> RetrievalSystem:
    templates = get_all_templates(vault_path)
    docs = get_all_notes(vault_path)
    return RetrievalSystem.build(templates, docs, index_dir=index_path)


if __name__ == "__main__":
    cli()
