from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from app.core.config import Settings
from app.core.errors import InvalidAgentRequest, TranscriptDataError
from app.schemas.runs import DayId


SEGMENT_PATTERN = re.compile(r"\[(T\d{2}-\d{3})\]")
VALID_DAYS: tuple[DayId, ...] = ("day_1", "day_2")


@dataclass(frozen=True)
class LoadedDay:
    day_id: DayId
    fingerprint: str
    documents: list[Document]
    files: list[Path]


class TranscriptLoader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.root = settings.agent_data_root.resolve()
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "header_1"),
                ("##", "header_2"),
                ("###", "header_3"),
            ],
            strip_headers=False,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.agent_chunk_size,
            chunk_overlap=settings.agent_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def day_directory(self, day_id: DayId) -> Path:
        if day_id not in VALID_DAYS:
            raise InvalidAgentRequest(f"Unsupported day_id: {day_id}")
        target = (self.root / day_id).resolve()
        if target.parent != self.root:
            raise InvalidAgentRequest("Invalid transcript directory")
        return target

    def list_files(self, day_id: DayId) -> list[Path]:
        directory = self.day_directory(day_id)
        if not directory.is_dir():
            raise TranscriptDataError(
                f"Transcript folder does not exist for {day_id}"
            )
        files = sorted(path for path in directory.rglob("*.md") if path.is_file())
        if not files:
            raise TranscriptDataError(f"No Markdown transcripts found for {day_id}")
        return files

    def fingerprint(self, day_id: DayId) -> str:
        digest = hashlib.sha256()
        for path in self.list_files(day_id):
            relative = path.relative_to(self.root).as_posix()
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def load_day(self, day_id: DayId) -> LoadedDay:
        files = self.list_files(day_id)
        fingerprint = self.fingerprint(day_id)
        documents: list[Document] = []

        for path in files:
            source = path.name
            markdown = path.read_text(encoding="utf-8")
            header_documents = self.header_splitter.split_text(markdown)
            chunk_number = 0

            for header_document in header_documents:
                splits = self.text_splitter.split_documents([header_document])
                for split in splits:
                    segment_ids = SEGMENT_PATTERN.findall(split.page_content)
                    heading = self._best_heading(split.metadata)
                    split.metadata.update(
                        {
                            "day_id": day_id,
                            "source": source,
                            "source_path": path.relative_to(self.root).as_posix(),
                            "heading": heading,
                            "segment_ids": ",".join(segment_ids),
                            "chunk_number": chunk_number,
                        }
                    )
                    documents.append(split)
                    chunk_number += 1

        if not documents:
            raise TranscriptDataError(f"No readable transcript content for {day_id}")

        return LoadedDay(
            day_id=day_id,
            fingerprint=fingerprint,
            documents=documents,
            files=files,
        )

    @staticmethod
    def _best_heading(metadata: dict) -> str:
        return str(
            metadata.get("header_3")
            or metadata.get("header_2")
            or metadata.get("header_1")
            or ""
        )


def document_id(document: Document) -> str:
    material = "|".join(
        [
            str(document.metadata.get("day_id", "")),
            str(document.metadata.get("source_path", "")),
            str(document.metadata.get("chunk_number", "")),
            document.page_content,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
