from dataclasses import dataclass
from typing import Iterable
from uuid import uuid4

from pathlib import Path

from isort import file


@dataclass(frozen=True)
class Template:
    id: str
    content: str
    path: Path


@dataclass(frozen=True)
class MarkdownNote:
    id: str
    path: Path

    title: str
    aliases: list[str]
    headings: list[str]

    body: str


def chunk_markdown(text, max_chunk_size=1000):
    """
    Split the markdown input by all headers, hlines and if the max_chars per chunk is reached (mxax_chunk_size).

    Args:
        text (str): The markdown text to be chunked.
        max_chunk_size (int): The maximum number of characters allowed in each chunk.

    Returns:
        list: A list of markdown chunks.
    """

    chunks = []
    current_chunk = ""

    lines = text.splitlines()
    for line in lines:
        # Check if the line is a header or a horizontal line
        if line.startswith("#") or line.startswith("---") or len(current_chunk) + len(line) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        current_chunk += line + "\n"

    # Add any remaining content as a chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def get_all_notes(vault_path: Path) -> list[MarkdownNote]:
    """Return paths of all markdown files in the vault."""
    results = []

    for file in vault_path.rglob("*.md"):

        body = file.read_text()
        headings = [line for line in body.splitlines() if line.startswith("#")]

        mdNote = MarkdownNote(
            id = uuid4().hex,
            path=file,
            title=file.stem,
            aliases=[],
            body=body,
            headings=headings,
        )

        results.append(mdNote)
        
    return results

def get_all_templates(vault_path: Path) -> Iterable[Template]:
    """
    Get all templates from the vault.

    Templates are everything tagged with #template, as well as all files in the "Templates" folder.

    Args:
        vault_path (Path): vault root path.
    
    Returns:
        list: A list of template file paths.
    """
    templates = []

    # Search for files tagged with #template
    for file in vault_path.rglob("*.md"):
        with file.open() as f:
            content = f.read()
            if "#template" in content:
                template = Template(
                    id = uuid4().hex,
                    path=file,
                    content=content,
                )
                templates.append(template)

    # Search for files in the "Templates" folder
    templates_folder = vault_path / "Templates"
    if templates_folder.exists():
        for file in templates_folder.rglob("*.md"):
            with file.open() as f:
                content = f.read()
                template = Template(
                    id = uuid4().hex,
                    path=file,
                    content=content,
                )
                templates.append(template)

    return templates
