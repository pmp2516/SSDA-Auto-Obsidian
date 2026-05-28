from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Self

import numpy as np
import torch

import pyterrier as pt

from transformers import AutoModel, AutoTokenizer


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


class SentenceEncoder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModel.from_pretrained(model_name).to(self.device)

        self.model.eval()

    @torch.no_grad()
    def encode(
        self,
        texts: Sequence[str],
    ) -> np.ndarray:
        batch = self.tokenizer(
            list(texts),
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        outputs = self.model(**batch)

        hidden = outputs.last_hidden_state

        mask = batch["attention_mask"].unsqueeze(-1).expand(hidden.shape)

        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)

        pooled = torch.nn.functional.normalize(
            pooled,
            p=2,
            dim=1,
        )

        return pooled.cpu().numpy()


class TemplateIndex:
    def __init__(
        self,
        encoder: SentenceEncoder,
        templates: list[Template],
        embeddings: np.ndarray,
    ):
        self.encoder = encoder
        self.templates = templates
        self.embeddings = embeddings

    @classmethod
    def build(
        cls,
        templates: Iterable[Template],
    ) -> Self:
        encoder = SentenceEncoder()

        templates = list(templates)

        embeddings = encoder.encode([t.content for t in templates])

        return cls(
            encoder=encoder,
            templates=templates,
            embeddings=embeddings,
        )

    def retrieve(
        self,
        query: str,
    ) -> Template:
        query_embedding = self.encoder.encode([query])[0]

        scores = self.embeddings @ query_embedding

        idx = int(np.argmax(scores))

        return self.templates[idx]


class MarkdownLinkIndex:
    FIELD_BOOSTS = {
        "title": 5.0,
        "aliases": 4.0,
        "headings": 2.0,
        "body": 1.0,
    }

    def __init__(
        self,
        searcher: pt.terrier.Retriever,
    ):
        self.searcher = searcher

    @classmethod
    def build(
        cls,
        notes: Iterable[MarkdownNote],
        index_dir: str | Path,
    ) -> Self:
        index_dir = Path(index_dir)

        index = pt.terrier.TerrierIndex(str(index_dir))
        indexer = index.indexer(meta={"docno": 32})

        indexer.index([
            {
                "docno": note.id,
                "text": note.body,
                "title": note.title,
                "aliases": " ".join(note.aliases),
                "headings": "\n".join(note.headings),
                "path": str(note.path),
            }
            for note in notes
        ])

        searcher = index.retriever('BM25') % 1

        return cls(searcher)

    @classmethod
    def _build_query(
        cls,
        text: str,
    ) -> str:
        return " ".join(
            f'{field}:("{text}")^{boost}' for field, boost in cls.FIELD_BOOSTS.items()
        )

    def search_span(
        self,
        text: str,
    ) -> list[dict]:
        hits = self.searcher.search(text)

        results = []

        for hit in hits.iterrows():
            results.append(hit)

        return results


class RetrievalSystem:
    def __init__(
        self,
        template_index: TemplateIndex,
        link_index: MarkdownLinkIndex,
    ):
        self.template_index = template_index
        self.link_index = link_index

    @classmethod
    def build(
        cls,
        templates: Iterable[Template],
        notes: Iterable[MarkdownNote],
        *,
        index_dir: str | Path,
    ) -> Self:
        index_dir = Path(index_dir)
        return cls(
            template_index=TemplateIndex.build(templates),
            link_index=MarkdownLinkIndex.build(
                notes,
                index_dir=index_dir,
            ),
        )

    def retrieve_template(
        self,
        text: str,
    ) -> Template:
        return self.template_index.retrieve(text)

    def propose_links(
        self,
        spans: Iterable[tuple[int, int, str]],
    ) -> list[tuple[int, int, list[dict]]]:
        return [
            (
                *span[:2],
                self.link_index.search_span(
                    span[2],
                ),
            )
            for span in spans
        ]
