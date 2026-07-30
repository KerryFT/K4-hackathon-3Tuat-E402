from typing import Any, TypedDict

from app.schemas.runs import DayId, RunMode


class AgentState(TypedDict, total=False):
    day_id: DayId
    mode: RunMode
    query: str | None
    messages: list[Any]
    fingerprint: str
    retrieved_context: list[dict]
    citations: list[dict]
    answer: str
    error: str | None
