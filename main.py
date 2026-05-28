import click
from pathlib import Path


@click.group()
def cli():
    """Auto-Obsidian: OCR-to-vault pipeline."""
    pass


@cli.command("add-note")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True), help="Path to the input image.")
@click.option("--vault", required=True, type=click.Path(), help="Path to the Obsidian vault.")
def add_note(input_path: str, vault: str):
    """Process a handwritten image and write a new note into the vault."""
    image_path = Path(input_path)
    vault_path = Path(vault)

    click.echo(f"Processing image: {image_path}")

    extracted = _run_ocr(image_path)
    click.echo("OCR complete.")

    template = _retrieve_template(extracted)
    click.echo(f"Matched template: {template['name']}")

    note_content = _render_note(extracted, template)

    _write_note(note_content, vault_path)
    click.echo(f"Note written to vault: {vault_path}")


@cli.command("update-index")
@click.option("--vault", required=True, type=click.Path(exists=True), help="Path to the Obsidian vault.")
def update_index(vault: str):
    """Scan the vault and rebuild the Qdrant template index."""
    vault_path = Path(vault)
    click.echo(f"Scanning vault: {vault_path}")

    _rebuild_index(vault_path)
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


def _retrieve_template(extracted: dict) -> dict:
    """Query Qdrant for the best-matching note template.

    Args:
        extracted: output of _run_ocr

    Returns a dict with at least:
        name     (str) — template identifier
        content  (str) — raw template markdown
    """
    # TODO: embed extracted['tags'] / extracted['text'], query Qdrant collection,
    #       return the top-1 result payload as the template dict

    # TODO: consider which threshold (if any) is appropriate for our demo case

    # TODO: Fallback will be just an empty note, I guess
    raise NotImplementedError("Template retrieval from Qdrant not yet implemented")


def _render_note(extracted: dict, template: dict) -> str:
    """Merge OCR output into the template to produce the final note markdown.

    Args:
        extracted: output of _run_ocr
        template:  output of _retrieve_template

    Returns the complete note as a markdown string.
    """
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


def _rebuild_index(vault_path: Path) -> None:
    """Scan the vault, embed all templates, and upsert them into Qdrant.

    Should be idempotent — running twice must not create duplicate vectors.
    """
    # TODO: walk vault_path for *.md files, embed each with a chosen model,
    #       upsert into a Qdrant collection keyed by file path hash
    raise NotImplementedError("Index builder not yet implemented")


if __name__ == "__main__":
    cli()
