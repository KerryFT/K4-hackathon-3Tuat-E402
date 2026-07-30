from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.core.config import Settings
from app.services.documents import TranscriptLoader
from app.tools.transcripts import TranscriptTools


class FakeProvider:
    def __init__(self):
        self.calls = 0

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        return f"generated-{self.calls}"

    def embeddings(self):
        raise AssertionError("Embeddings are not needed in this test")


class FakeIndex:
    async def ensure_index(self, day_id: str) -> str:
        return "fingerprint"

    async def retrieve(self, day_id: str, query: str):
        return [
            Document(
                page_content="Grounded content",
                metadata={
                    "day_id": day_id,
                    "source": "lesson.md",
                    "heading": "Topic",
                    "segment_ids": "T04-001",
                },
            )
        ]


def make_tools(tmp_path: Path):
    data_root = tmp_path / "transcript"
    (data_root / "day_1").mkdir(parents=True)
    (data_root / "day_1" / "lesson.md").write_text(
        "# Foundation\n\n## Topic\n\n[T04-001] Grounded content.",
        encoding="utf-8",
    )
    settings = Settings(
        _env_file=None,
        agent_data_root=data_root,
        agent_chroma_dir=tmp_path / "chroma",
        agent_summary_cache_dir=tmp_path / "summaries",
        agent_chunk_size=500,
        agent_chunk_overlap=50,
        agent_summary_batch_chars=5000,
    )
    provider = FakeProvider()
    return (
        TranscriptTools(
            settings,
            TranscriptLoader(settings),
            FakeIndex(),
            provider,
        ),
        provider,
    )


@pytest.mark.asyncio
async def test_summary_cache_avoids_repeated_model_calls(tmp_path: Path):
    tools, provider = make_tools(tmp_path)

    first_answer, first_citations = await tools.summarize_day_transcripts("day_1")
    calls_after_first = provider.calls
    second_answer, second_citations = await tools.summarize_day_transcripts(
        "day_1"
    )

    assert calls_after_first >= 2
    assert provider.calls == calls_after_first
    assert second_answer == first_answer
    assert second_citations == first_citations
    assert "lesson.md" in first_answer


@pytest.mark.asyncio
async def test_retrieval_citations_are_structured(tmp_path: Path):
    tools, _ = make_tools(tmp_path)
    context, citations = await tools.retrieve_day_transcripts(
        "day_1", "attention"
    )

    assert context[0]["source"] == "lesson.md"
    assert citations[0].segment_ids == ["T04-001"]
