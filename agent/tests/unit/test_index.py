from pathlib import Path

import pytest
from langchain_core.embeddings import Embeddings

from app.core.config import Settings
from app.core.errors import ModelConfigurationError
from app.services.documents import TranscriptLoader
from app.services.index import TranscriptIndexManager


class KeywordEmbeddings(Embeddings):
    @staticmethod
    def _embed(text: str) -> list[float]:
        lowered = text.lower()
        return [
            float(lowered.count("foundation")),
            float(lowered.count("product")),
            1.0,
        ]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def make_settings(tmp_path: Path) -> Settings:
    data_root = tmp_path / "transcript"
    (data_root / "day_1").mkdir(parents=True)
    (data_root / "day_2").mkdir(parents=True)
    (data_root / "day_1" / "d1.md").write_text(
        "# Foundation\n[T04-001] foundation attention model",
        encoding="utf-8",
    )
    (data_root / "day_2" / "d2.md").write_text(
        "# Product\n[T01-001] product metric automation",
        encoding="utf-8",
    )
    return Settings(
        _env_file=None,
        agent_data_root=data_root,
        agent_chroma_dir=tmp_path / "chroma",
        agent_summary_cache_dir=tmp_path / "summaries",
        agent_chunk_size=500,
        agent_chunk_overlap=50,
    )


@pytest.mark.asyncio
async def test_retrieval_never_crosses_day_collections(tmp_path: Path):
    settings = make_settings(tmp_path)
    manager = TranscriptIndexManager(
        settings,
        TranscriptLoader(settings),
        embedding_factory=KeywordEmbeddings,
    )

    day_1_results = await manager.retrieve("day_1", "product")
    day_2_results = await manager.retrieve("day_2", "foundation")

    assert day_1_results
    assert day_2_results
    assert {doc.metadata["day_id"] for doc in day_1_results} == {"day_1"}
    assert {doc.metadata["day_id"] for doc in day_2_results} == {"day_2"}


@pytest.mark.asyncio
async def test_unchanged_fingerprint_reuses_index(tmp_path: Path):
    settings = make_settings(tmp_path)
    manager = TranscriptIndexManager(
        settings,
        TranscriptLoader(settings),
        embedding_factory=KeywordEmbeddings,
    )

    first = await manager.ensure_index("day_1")
    second = await manager.ensure_index("day_1")

    assert first == second
    assert manager.status("day_1")["indexed"] is True


@pytest.mark.asyncio
async def test_model_configuration_error_is_not_hidden(tmp_path: Path):
    settings = make_settings(tmp_path)

    def missing_credentials():
        raise ModelConfigurationError("OpenAI is not configured")

    manager = TranscriptIndexManager(
        settings,
        TranscriptLoader(settings),
        embedding_factory=missing_credentials,
    )

    with pytest.raises(ModelConfigurationError, match="not configured"):
        await manager.ensure_index("day_1")
