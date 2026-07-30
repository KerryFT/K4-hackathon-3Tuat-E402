from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.core.errors import InvalidAgentRequest
from app.models.state import AgentState
from app.services.documents import VALID_DAYS
from app.tools.transcripts import TranscriptTools


def build_graph(tools: TranscriptTools):
    async def validate(state: AgentState) -> dict:
        day_id = state.get("day_id")
        mode = state.get("mode")
        query = state.get("query")

        if day_id not in VALID_DAYS:
            raise InvalidAgentRequest("day_id must be 'day_1' or 'day_2'")
        if mode not in ("summary", "qa"):
            raise InvalidAgentRequest("mode must be 'summary' or 'qa'")
        if mode == "qa" and (
            not isinstance(query, str) or not query.strip()
        ):
            raise InvalidAgentRequest("query is required when mode='qa'")
        return {
            "query": query.strip() if mode == "qa" else None,
            "messages": state.get("messages", []),
            "error": None,
        }

    async def ensure_index(state: AgentState) -> dict:
        fingerprint = await tools.ensure_index(state["day_id"])
        return {"fingerprint": fingerprint}

    def route_mode(state: AgentState) -> Literal["summarize", "retrieve"]:
        return "summarize" if state["mode"] == "summary" else "retrieve"

    async def summarize(state: AgentState) -> dict:
        answer, citations = await tools.summarize_day_transcripts(
            state["day_id"]
        )
        return {
            "answer": answer,
            "citations": [
                citation.model_dump() for citation in citations
            ],
        }

    async def retrieve(state: AgentState) -> dict:
        context, citations = await tools.retrieve_day_transcripts(
            state["day_id"],
            state["query"] or "",
        )
        return {
            "retrieved_context": context,
            "citations": [
                citation.model_dump() for citation in citations
            ],
        }

    async def answer(state: AgentState) -> dict:
        from app.schemas.runs import Citation

        citations = [
            Citation.model_validate(citation)
            for citation in state.get("citations", [])
        ]
        result = await tools.answer_from_context(
            day_id=state["day_id"],
            query=state["query"] or "",
            context=state.get("retrieved_context", []),
            citations=citations,
        )
        return {"answer": result}

    builder = StateGraph(AgentState)
    builder.add_node("validate", validate)
    builder.add_node("ensure_index", ensure_index)
    builder.add_node("summarize", summarize)
    builder.add_node("retrieve", retrieve)
    builder.add_node("answer", answer)

    builder.add_edge(START, "validate")
    builder.add_edge("validate", "ensure_index")
    builder.add_conditional_edges(
        "ensure_index",
        route_mode,
        {
            "summarize": "summarize",
            "retrieve": "retrieve",
        },
    )
    builder.add_edge("summarize", END)
    builder.add_edge("retrieve", "answer")
    builder.add_edge("answer", END)
    return builder.compile()
