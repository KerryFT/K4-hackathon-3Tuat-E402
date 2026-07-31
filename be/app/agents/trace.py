from dataclasses import dataclass


@dataclass(frozen=True)
class AgentTrace:
    """Internal, per-run measurements used by the offline evaluation runner."""

    scope: str = "all_lectures"
    requested_lecture_ids: tuple[str, ...] = ()
    retrieved_source_ids: tuple[str, ...] = ()
    retrieved_lecture_ids: tuple[str, ...] = ()
    context_chars: int = 0
    context_character_budget: int = 0
