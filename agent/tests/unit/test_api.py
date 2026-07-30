from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.graph import build_graph
from app.main import create_app
from app.schemas.runs import Citation


class FakeIndex:
    def status(self, day_id: str):
        return {"available": True, "indexed": day_id == "day_1"}


class FakeTools:
    async def ensure_index(self, day_id: str) -> str:
        return "abc"

    async def summarize_day_transcripts(self, day_id: str):
        return (
            f"Summary {day_id}",
            [Citation(source="lesson.md", segment_ids=["T04-001"])],
        )

    async def retrieve_day_transcripts(self, day_id: str, query: str):
        return (
            [
                {
                    "content": "Context",
                    "source": "lesson.md",
                    "heading": "Topic",
                    "segment_ids": ["T04-001"],
                }
            ],
            [Citation(source="lesson.md", segment_ids=["T04-001"])],
        )

    async def answer_from_context(
        self, day_id: str, query: str, context: list[dict], citations: list
    ):
        return f"Answer {day_id}"


def make_client() -> TestClient:
    settings = SimpleNamespace(
        openai_configured=True,
        openai_model="test-model",
        openai_embedding_model="test-embedding",
    )
    runtime = SimpleNamespace(
        settings=settings,
        index_manager=FakeIndex(),
        graph=build_graph(FakeTools()),
    )
    return TestClient(create_app(runtime))


def test_health_reports_both_days_without_secrets():
    response = make_client().get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload["days"]) == {"day_1", "day_2"}
    assert payload["model"]["configured"] is True
    assert "api_key" not in response.text.lower()


def test_summary_stream_has_status_tokens_sources_and_done():
    response = make_client().post(
        "/internal/v1/agent-runs/stream",
        json={"day_id": "day_1", "mode": "summary", "query": None},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert body.index("event: status") < body.index("event: token")
    assert body.index("event: token") < body.index("event: sources")
    assert body.index("event: sources") < body.index("event: done")
    assert "Summary day_1" in body
    assert "T04-001" in body


def test_qa_requires_non_empty_query():
    response = make_client().post(
        "/internal/v1/agent-runs/stream",
        json={"day_id": "day_1", "mode": "qa", "query": "  "},
    )
    assert response.status_code == 422


def test_unknown_fields_are_rejected():
    response = make_client().post(
        "/internal/v1/agent-runs/stream",
        json={
            "day_id": "day_1",
            "mode": "summary",
            "path": "../../day_2",
        },
    )
    assert response.status_code == 422
