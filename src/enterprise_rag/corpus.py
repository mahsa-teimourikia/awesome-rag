from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import re
from typing import Iterable

@dataclass(frozen=True)
class Document:
    id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)

def load_corpus(data_dir: str | Path = "data/enterprise") -> list[Document]:
    base = Path(data_dir)
    docs: list[Document] = []
    for path in sorted(base.rglob("*")):
        if path.suffix.lower() not in {".md", ".csv"}:
            continue
        rel = path.relative_to(base).as_posix()
        if path.suffix == ".csv":
            rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
            text = "\n".join(" | ".join(f"{k}: {v}" for k, v in row.items()) for row in rows)
        else:
            text = path.read_text(encoding="utf-8")
        docs.append(Document(id=rel, text=text, metadata={"source": rel, "domain": rel.split("/")[0]}))
    return docs

def _sections(text: str) -> Iterable[tuple[str, str]]:
    current = "Introduction"
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            if buf:
                yield current, "\n".join(buf).strip()
                buf = []
            current = re.sub(r"^#+\s*", "", line).strip() or current
        else:
            buf.append(line)
    if buf:
        yield current, "\n".join(buf).strip()

def chunk_documents(docs: list[Document], strategy: str = "structure", max_words: int = 80) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        parts = list(_sections(doc.text)) if strategy == "structure" else [("fixed", doc.text)]
        for section, body in parts:
            words = body.split()
            if not words:
                continue
            windows = [words[i:i+max_words] for i in range(0, len(words), max_words)] if strategy == "fixed" else [words]
            for idx, window in enumerate(windows, start=1):
                cid = f"{doc.id}#{section.lower().replace(' ', '-')}-{idx}"
                chunks.append(Chunk(cid, doc.id, " ".join(window), {**doc.metadata, "section": section}))
    return chunks
