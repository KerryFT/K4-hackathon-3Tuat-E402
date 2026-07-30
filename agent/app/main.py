from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.core.errors import AgentError
from app.runtime import AgentRuntime, create_runtime
from app.schemas.runs import AgentRunRequest, Citation
from app.services.documents import VALID_DAYS


logger = logging.getLogger(__name__)


def create_app(runtime: AgentRuntime | None = None) -> FastAPI:
    app = FastAPI(
        title="Transcript Agent",
        version="0.1.0",
        docs_url="/internal/docs",
        openapi_url="/internal/openapi.json",
    )
    app.state.runtime = runtime or create_runtime()

    @app.get("/health")
    async def health() -> dict[str, Any]:
        active_runtime: AgentRuntime = app.state.runtime
        settings = active_runtime.settings
        return {
            "status": "ok",
            "service": "agent",
            "model": {
                "configured": settings.openai_configured,
                "chat": settings.openai_model or None,
                "embedding": settings.openai_embedding_model,
            },
            "days": {
                day_id: active_runtime.index_manager.status(day_id)
                for day_id in VALID_DAYS
            },
        }

    @app.post("/internal/v1/agent-runs/stream")
    async def stream_agent_run(
        request: AgentRunRequest,
    ) -> StreamingResponse:
        return StreamingResponse(
            _stream_graph(app.state.runtime, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return app


async def _stream_graph(
    runtime: AgentRuntime,
    request: AgentRunRequest,
) -> AsyncIterator[str]:
    yield _sse("status", {"stage": "loading", "day_id": request.day_id})
    yield _sse("status", {"stage": "indexing", "day_id": request.day_id})
    next_stage = "summarizing" if request.mode == "summary" else "retrieving"
    yield _sse("status", {"stage": next_stage, "day_id": request.day_id})

    final_state: dict[str, Any] = {}
    try:
        async for part in runtime.graph.astream(
            request.model_dump(),
            stream_mode="updates",
            version="v2",
        ):
            updates = _extract_updates(part)
            for node_name, node_update in updates.items():
                if not isinstance(node_update, dict):
                    continue
                final_state.update(node_update)
                if node_name == "retrieve":
                    yield _sse(
                        "status",
                        {"stage": "generating", "day_id": request.day_id},
                    )

        answer = str(final_state.get("answer", ""))
        citations = [
            Citation.model_validate(item)
            for item in final_state.get("citations", [])
        ]
        for delta in _text_chunks(answer):
            yield _sse("token", {"delta": delta})
        yield _sse(
            "sources",
            {
                "items": [
                    citation.model_dump() for citation in citations
                ]
            },
        )
        yield _sse(
            "done",
            {
                "day_id": request.day_id,
                "mode": request.mode,
            },
        )
    except AgentError as exc:
        yield _sse(
            "error",
            {
                "code": exc.code,
                "message": str(exc),
            },
        )
    except Exception:
        logger.exception("Unexpected agent run failure")
        yield _sse(
            "error",
            {
                "code": "INTERNAL_AGENT_ERROR",
                "message": "Agent could not complete the request",
            },
        )


def _extract_updates(part: Any) -> dict[str, Any]:
    if not isinstance(part, dict):
        return {}
    if part.get("type") == "updates":
        data = part.get("data", {})
        return data if isinstance(data, dict) else {}
    return part


def _text_chunks(text: str, chunk_size: int = 120) -> list[str]:
    return [
        text[index : index + chunk_size]
        for index in range(0, len(text), chunk_size)
    ]


def _sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


app = create_app()
