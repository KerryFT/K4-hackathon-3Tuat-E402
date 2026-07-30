import json
import os
import re
from pathlib import Path

from app.providers.vector_store.in_memory import InMemoryVectorStore
from app.schemas.retrieval import SearchRequest, SourceChunk


class JsonlVectorStore:
    """Persistent development index backed by JSONL and lexical retrieval."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._memory = InMemoryVectorStore()
        self._chunks: dict[str, SourceChunk] = {}
        if path.exists():
            self._load()

    def _load(self) -> None:
        chunks: list[SourceChunk] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    chunk = SourceChunk.model_validate_json(line)
                except Exception as exc:
                    raise ValueError(
                        f"Invalid chunk at {self.path}:{line_number}"
                    ) from exc
                chunks.append(chunk)
        self._replace_memory(chunks)

    def _replace_memory(self, chunks: list[SourceChunk]) -> None:
        self._chunks = {chunk.source_id: chunk for chunk in chunks}
        self._memory = InMemoryVectorStore()
        self._memory.add(list(self._chunks.values()))

    def add(self, chunks: list[SourceChunk]) -> None:
        merged = dict(self._chunks)
        merged.update({chunk.source_id: chunk for chunk in chunks})
        ordered = sorted(merged.values(), key=_chunk_sort_key)
        self._replace_memory(ordered)
        self._persist()

    def replace(self, chunks: list[SourceChunk]) -> None:
        self._replace_memory(sorted(chunks, key=_chunk_sort_key))
        self._persist()

    def search(self, request: SearchRequest) -> list[SourceChunk]:
        return self._memory.search(request)

    def all_chunks(self) -> list[SourceChunk]:
        return list(self._chunks.values())

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            for chunk in self._chunks.values():
                handle.write(chunk.model_dump_json())
                handle.write("\n")
        os.replace(temporary, self.path)


def _chunk_sort_key(chunk: SourceChunk) -> tuple[str, int, int]:
    match = re.search(r":(\d+)$", chunk.source_id)
    chunk_number = int(match.group(1)) if match else 0
    return chunk.lecture_id, chunk.page or 0, chunk_number
