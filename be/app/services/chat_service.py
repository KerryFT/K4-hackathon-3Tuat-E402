import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.agents.tutor_agent import TutorAgent, tutor_agent
from app.core.config import BACKEND_DIR, settings
from app.repositories.conversation_log_repository import ConversationLogRepository
from app.schemas.chat import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        agent: TutorAgent,
        log_repository: ConversationLogRepository,
    ) -> None:
        self.agent = agent
        self.log_repository = log_repository

    def reply(self, request: ChatRequest) -> ChatResponse:
        conversation_id = request.conversation_id or str(uuid4())
        normalized_request = request.model_copy(
            update={"conversation_id": conversation_id}
        )
        event_id = str(uuid4())
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        started_at = perf_counter()

        try:
            response = self.agent.run(normalized_request)
        except Exception as exc:
            self._append_event(
                {
                    "schema_version": 1,
                    "event_id": event_id,
                    "conversation_id": conversation_id,
                    "timestamp_utc": timestamp_utc,
                    "duration_ms": self._duration_ms(started_at),
                    "request": normalized_request.model_dump(mode="json"),
                    "response": None,
                    "trace": self._trace_payload(),
                    "error": {"type": type(exc).__name__},
                }
            )
            raise

        response = response.model_copy(
            update={"conversation_id": conversation_id}
        )
        self._append_event(
            {
                "schema_version": 1,
                "event_id": event_id,
                "conversation_id": conversation_id,
                "timestamp_utc": timestamp_utc,
                "duration_ms": self._duration_ms(started_at),
                "request": normalized_request.model_dump(mode="json"),
                "response": response.model_dump(mode="json"),
                "trace": self._trace_payload(),
                "error": None,
            }
        )
        return response

    def _append_event(self, event: dict[str, Any]) -> None:
        try:
            self.log_repository.append(event)
        except Exception:
            logger.exception(
                "Failed to persist conversation audit event %s",
                event["event_id"],
            )

    def _trace_payload(self) -> dict[str, Any]:
        trace = getattr(self.agent, "last_trace", None)
        if trace is None:
            return {}

        payload: dict[str, Any] = {}
        for field_name in (
            "scope",
            "requested_lecture_ids",
            "retrieved_source_ids",
            "retrieved_lecture_ids",
            "context_chars",
            "context_character_budget",
        ):
            if not hasattr(trace, field_name):
                continue
            value = getattr(trace, field_name)
            payload[field_name] = list(value) if isinstance(value, tuple) else value
        return payload

    @staticmethod
    def _duration_ms(started_at: float) -> int:
        return max(0, round((perf_counter() - started_at) * 1000))


conversation_log_path = Path(settings.conversation_log_dir)
if not conversation_log_path.is_absolute():
    conversation_log_path = BACKEND_DIR / conversation_log_path

conversation_log_repository = ConversationLogRepository(
    conversation_log_path.resolve(),
    enabled=settings.conversation_log_enabled,
)
chat_service = ChatService(tutor_agent, conversation_log_repository)
