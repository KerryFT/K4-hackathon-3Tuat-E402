from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document

from app.core.config import Settings
from app.prompts.templates import (
    QA_SYSTEM_PROMPT,
    QA_USER_PROMPT,
    SUMMARY_BATCH_PROMPT,
    SUMMARY_REDUCE_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
)
from app.schemas.runs import Citation, DayId
from app.services.documents import TranscriptLoader
from app.services.index import TranscriptIndexManager
from app.services.llm import ModelProvider


class TranscriptTools:
    """Day-scoped operations used as deterministic LangGraph tools."""

    def __init__(
        self,
        settings: Settings,
        loader: TranscriptLoader,
        index_manager: TranscriptIndexManager,
        model_provider: ModelProvider,
    ):
        self.settings = settings
        self.loader = loader
        self.index_manager = index_manager
        self.model_provider = model_provider
        self._summary_locks = {
            "day_1": asyncio.Lock(),
            "day_2": asyncio.Lock(),
        }

    async def ensure_index(self, day_id: DayId) -> str:
        return await self.index_manager.ensure_index(day_id)

    async def summarize_day_transcripts(
        self, day_id: DayId
    ) -> tuple[str, list[Citation]]:
        async with self._summary_locks[day_id]:
            fingerprint = self.loader.fingerprint(day_id)
            cached = self._read_summary_cache(day_id, fingerprint)
            if cached is not None:
                return cached

            loaded = self.loader.load_day(day_id)
            grouped: dict[str, list[Document]] = defaultdict(list)
            for document in loaded.documents:
                grouped[str(document.metadata["source"])].append(document)

            partials: list[str] = []
            for source, documents in grouped.items():
                for batch in self._batches(documents):
                    content = "\n\n".join(doc.page_content for doc in batch)
                    partials.append(
                        await self.model_provider.complete(
                            SUMMARY_SYSTEM_PROMPT,
                            SUMMARY_BATCH_PROMPT.format(
                                source=source,
                                content=content,
                            ),
                        )
                    )

            answer = await self.model_provider.complete(
                SUMMARY_SYSTEM_PROMPT,
                SUMMARY_REDUCE_PROMPT.format(
                    day_id=day_id,
                    partials="\n\n".join(
                        f"### Phần {index}\n{partial}"
                        for index, partial in enumerate(partials, start=1)
                    ),
                ),
            )
            citations = citations_from_documents(loaded.documents)
            answer = append_source_footer(answer, citations)
            self._write_summary_cache(
                day_id,
                loaded.fingerprint,
                answer,
                citations,
            )
            return answer, citations

    async def retrieve_day_transcripts(
        self, day_id: DayId, query: str
    ) -> tuple[list[dict], list[Citation]]:
        documents = await self.index_manager.retrieve(day_id, query)
        context = [
            {
                "content": document.page_content,
                "source": str(document.metadata.get("source", "")),
                "heading": str(document.metadata.get("heading", "")),
                "segment_ids": split_segment_ids(
                    str(document.metadata.get("segment_ids", ""))
                ),
            }
            for document in documents
        ]
        return context, citations_from_documents(documents)

    async def answer_from_context(
        self,
        day_id: DayId,
        query: str,
        context: list[dict],
        citations: list[Citation],
    ) -> str:
        rendered_context = "\n\n".join(
            (
                f"[Nguồn: {item['source']} | "
                f"heading: {item['heading'] or 'N/A'} | "
                f"mã đoạn: {', '.join(item['segment_ids']) or 'N/A'}]\n"
                f"{item['content']}"
            )
            for item in context
        )
        answer = await self.model_provider.complete(
            QA_SYSTEM_PROMPT,
            QA_USER_PROMPT.format(
                query=query,
                day_id=day_id,
                context=rendered_context,
            ),
        )
        return append_source_footer(answer, citations)

    def _batches(self, documents: list[Document]) -> list[list[Document]]:
        batches: list[list[Document]] = []
        current: list[Document] = []
        current_size = 0
        limit = self.settings.agent_summary_batch_chars

        for document in documents:
            document_size = len(document.page_content)
            if current and current_size + document_size > limit:
                batches.append(current)
                current = []
                current_size = 0
            current.append(document)
            current_size += document_size
        if current:
            batches.append(current)
        return batches

    def _cache_path(self, day_id: DayId) -> Path:
        return self.settings.agent_summary_cache_dir / f"{day_id}.json"

    def _read_summary_cache(
        self, day_id: DayId, fingerprint: str
    ) -> tuple[str, list[Citation]] | None:
        path = self._cache_path(day_id)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("fingerprint") != fingerprint:
                return None
            answer = str(payload["answer"])
            citations = [
                Citation.model_validate(item)
                for item in payload.get("citations", [])
            ]
            return answer, citations
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            return None

    def _write_summary_cache(
        self,
        day_id: DayId,
        fingerprint: str,
        answer: str,
        citations: list[Citation],
    ) -> None:
        path = self._cache_path(day_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(
                {
                    "fingerprint": fingerprint,
                    "answer": answer,
                    "citations": [
                        citation.model_dump() for citation in citations
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        temporary_path.replace(path)


def split_segment_ids(value: str) -> list[str]:
    return [segment for segment in value.split(",") if segment]


def citations_from_documents(documents: list[Document]) -> list[Citation]:
    grouped: dict[tuple[str, str], list[str]] = {}
    for document in documents:
        source = str(document.metadata.get("source", ""))
        heading = str(document.metadata.get("heading", ""))
        key = (source, heading)
        grouped.setdefault(key, [])
        for segment_id in split_segment_ids(
            str(document.metadata.get("segment_ids", ""))
        ):
            if segment_id not in grouped[key]:
                grouped[key].append(segment_id)

    return [
        Citation(
            source=source,
            heading=heading or None,
            segment_ids=segment_ids,
        )
        for (source, heading), segment_ids in grouped.items()
    ]


def append_source_footer(answer: str, citations: list[Citation]) -> str:
    if not citations:
        return answer
    lines: list[str] = []
    for citation in citations:
        if citation.segment_ids:
            if len(citation.segment_ids) == 1:
                marker = f"[{citation.segment_ids[0]}]"
            else:
                marker = (
                    f"[{citation.segment_ids[0]}–{citation.segment_ids[-1]}]"
                )
        else:
            marker = "[không có mã đoạn]"
        heading = f" — {citation.heading}" if citation.heading else ""
        lines.append(f"- {citation.source}{heading} — {marker}")
    return f"{answer.rstrip()}\n\n## Nguồn truy xuất\n" + "\n".join(lines)
