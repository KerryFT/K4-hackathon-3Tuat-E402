from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.errors import TranscriptDataError
from app.services.documents import TranscriptLoader


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        agent_data_root=tmp_path / "transcript",
        agent_chroma_dir=tmp_path / "chroma",
        agent_summary_cache_dir=tmp_path / "summaries",
        agent_chunk_size=500,
        agent_chunk_overlap=50,
    )


def write_transcript(
    settings: Settings,
    day_id: str,
    filename: str,
    content: str,
) -> Path:
    directory = settings.agent_data_root / day_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


def test_loader_keeps_day_source_heading_and_segment_ids(tmp_path: Path):
    settings = make_settings(tmp_path)
    write_transcript(
        settings,
        "day_1",
        "lesson.md",
        "# Foundation\n\n## Attention\n\n"
        "**[T04-001]** Attention connects relevant tokens.\n\n"
        "**[T04-002]** Context matters.",
    )
    write_transcript(
        settings,
        "day_2",
        "other.md",
        "# Product\n\n**[T01-001]** This content belongs to day 2.",
    )

    loaded = TranscriptLoader(settings).load_day("day_1")

    assert loaded.day_id == "day_1"
    assert {doc.metadata["day_id"] for doc in loaded.documents} == {"day_1"}
    assert {doc.metadata["source"] for doc in loaded.documents} == {"lesson.md"}
    assert any(doc.metadata["heading"] == "Attention" for doc in loaded.documents)
    assert "T04-001" in ",".join(
        str(doc.metadata["segment_ids"]) for doc in loaded.documents
    )
    assert all("day 2" not in doc.page_content for doc in loaded.documents)


def test_fingerprint_changes_only_when_selected_day_changes(tmp_path: Path):
    settings = make_settings(tmp_path)
    day_1 = write_transcript(
        settings, "day_1", "one.md", "# One\n[T04-001] original"
    )
    day_2 = write_transcript(
        settings, "day_2", "two.md", "# Two\n[T01-001] original"
    )
    loader = TranscriptLoader(settings)

    before = loader.fingerprint("day_1")
    day_2.write_text("# Two\n[T01-001] changed", encoding="utf-8")
    assert loader.fingerprint("day_1") == before

    day_1.write_text("# One\n[T04-001] changed", encoding="utf-8")
    assert loader.fingerprint("day_1") != before


def test_missing_or_empty_day_folder_has_clear_error(tmp_path: Path):
    settings = make_settings(tmp_path)
    with pytest.raises(TranscriptDataError, match="does not exist"):
        TranscriptLoader(settings).load_day("day_1")

    (settings.agent_data_root / "day_1").mkdir(parents=True)
    with pytest.raises(TranscriptDataError, match="No Markdown"):
        TranscriptLoader(settings).load_day("day_1")
