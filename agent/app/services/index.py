from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.config import Settings
from app.core.errors import AgentError, IndexBuildError
from app.schemas.runs import DayId
from app.services.documents import (
    VALID_DAYS,
    TranscriptLoader,
    document_id,
)


EmbeddingFactory = Callable[[], Embeddings]


class TranscriptIndexManager:
    def __init__(
        self,
        settings: Settings,
        loader: TranscriptLoader,
        embedding_factory: EmbeddingFactory,
    ):
        self.settings = settings
        self.loader = loader
        self.embedding_factory = embedding_factory
        self.persist_directory = settings.agent_chroma_dir
        self.manifest_path = self.persist_directory / "manifest.json"
        self._locks = {day_id: asyncio.Lock() for day_id in VALID_DAYS}
        self._manifest_lock = threading.Lock()
        self._stores: dict[DayId, Chroma] = {}

    async def ensure_index(self, day_id: DayId) -> str:
        async with self._locks[day_id]:
            try:
                return await asyncio.to_thread(self._ensure_index_sync, day_id)
            except Exception as exc:
                if isinstance(exc, AgentError):
                    raise
                raise IndexBuildError(
                    f"Could not build transcript index for {day_id}"
                ) from exc

    async def retrieve(
        self, day_id: DayId, query: str, top_k: int | None = None
    ) -> list[Document]:
        await self.ensure_index(day_id)
        k = top_k or self.settings.agent_retrieval_top_k
        try:
            return await asyncio.to_thread(
                self._stores[day_id].similarity_search,
                query,
                k,
            )
        except Exception as exc:
            raise IndexBuildError(
                f"Could not query transcript index for {day_id}"
            ) from exc

    def status(self, day_id: DayId) -> dict[str, Any]:
        try:
            current_fingerprint = self.loader.fingerprint(day_id)
            with self._manifest_lock:
                manifest = self._read_manifest()
            indexed_fingerprint = manifest.get(day_id)
            return {
                "available": True,
                "indexed": indexed_fingerprint == current_fingerprint,
                "fingerprint": current_fingerprint[:12],
            }
        except Exception as exc:
            return {
                "available": False,
                "indexed": False,
                "error": str(exc),
            }

    def _ensure_index_sync(self, day_id: DayId) -> str:
        fingerprint = self.loader.fingerprint(day_id)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(self.persist_directory))
        collection_name = self._collection_name(day_id)
        with self._manifest_lock:
            manifest = self._read_manifest()
        collection_exists = collection_name in {
            collection.name for collection in client.list_collections()
        }

        if manifest.get(day_id) == fingerprint and collection_exists:
            collection = client.get_collection(collection_name)
            if collection.count() > 0:
                self._stores[day_id] = self._new_store(
                    day_id, client=client
                )
                return fingerprint

        if collection_exists:
            client.delete_collection(collection_name)

        loaded = self.loader.load_day(day_id)
        store = self._new_store(day_id, client=client)
        ids = [document_id(document) for document in loaded.documents]
        store.add_documents(documents=loaded.documents, ids=ids)
        self._stores[day_id] = store

        with self._manifest_lock:
            latest_manifest = self._read_manifest()
            latest_manifest[day_id] = loaded.fingerprint
            self._write_manifest(latest_manifest)
        return loaded.fingerprint

    def _new_store(
        self, day_id: DayId, client: chromadb.ClientAPI
    ) -> Chroma:
        return Chroma(
            client=client,
            collection_name=self._collection_name(day_id),
            embedding_function=self.embedding_factory(),
            collection_metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _collection_name(day_id: DayId) -> str:
        return f"transcripts_{day_id}"

    def _read_manifest(self) -> dict[str, str]:
        if not self.manifest_path.is_file():
            return {}
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return {
            key: value
            for key, value in data.items()
            if key in VALID_DAYS and isinstance(value, str)
        }

    def _write_manifest(self, manifest: dict[str, str]) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.manifest_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.manifest_path)
