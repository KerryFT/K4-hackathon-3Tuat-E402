import json
import tempfile
import unittest
from pathlib import Path

from app.agents.trace import AgentTrace
from app.repositories.conversation_log_repository import ConversationLogRepository
from app.schemas.chat import ChatRequest, ChatResponse, LearningContext
from app.services.chat_service import ChatService


class StubAgent:
    def __init__(self) -> None:
        self.last_trace = AgentTrace(
            scope="current_page",
            retrieved_source_ids=("day-01:5:0",),
            retrieved_lecture_ids=("day-01",),
            context_chars=420,
            context_character_budget=18000,
        )

    def run(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            answer=f"Trả lời cho: {request.message}",
            status="answered",
            scope="current_page",
        )


class FailingAgent:
    last_trace = AgentTrace(scope="all_lectures")

    def run(self, request: ChatRequest) -> ChatResponse:
        raise RuntimeError("synthetic failure")


class BrokenLogRepository:
    def append(self, event) -> None:
        raise OSError("disk unavailable")


class ConversationLogRepositoryTests(unittest.TestCase):
    def test_appends_utf8_jsonl_events_to_one_hashed_session_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = ConversationLogRepository(Path(temporary_directory))
            event = {
                "conversation_id": "../../phiên-tiếng-việt",
                "message": "Giải thích bài này",
            }

            repository.append(event)
            repository.append({**event, "message": "Câu tiếp theo"})

            files = list(Path(temporary_directory).glob("*.jsonl"))
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].parent, Path(temporary_directory))
            records = [
                json.loads(line)
                for line in files[0].read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(
                [record["message"] for record in records],
                ["Giải thích bài này", "Câu tiếp theo"],
            )
            self.assertEqual(records[0]["conversation_id"], "../../phiên-tiếng-việt")

    def test_disabled_repository_does_not_create_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_directory = Path(temporary_directory) / "logs"
            repository = ConversationLogRepository(log_directory, enabled=False)

            repository.append({"conversation_id": "disabled"})

            self.assertFalse(log_directory.exists())


class ChatServiceLoggingTests(unittest.TestCase):
    def test_successful_reply_is_logged_with_response_and_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = ConversationLogRepository(Path(temporary_directory))
            service = ChatService(StubAgent(), repository)

            response = service.reply(
                ChatRequest(
                    message="Problem statement là gì?",
                    conversation_id="demo-01",
                    context=LearningContext(
                        course_id="comp2010-phase-1",
                        current_lecture_id="day-01",
                        current_page=5,
                    ),
                )
            )

            self.assertEqual(response.conversation_id, "demo-01")
            log_file = next(Path(temporary_directory).glob("*.jsonl"))
            record = json.loads(log_file.read_text(encoding="utf-8"))
            self.assertEqual(record["schema_version"], 1)
            self.assertEqual(record["request"]["message"], "Problem statement là gì?")
            self.assertEqual(record["response"]["status"], "answered")
            self.assertEqual(
                record["trace"]["retrieved_source_ids"],
                ["day-01:5:0"],
            )
            self.assertIsNone(record["error"])
            self.assertGreaterEqual(record["duration_ms"], 0)

    def test_missing_conversation_id_is_generated_and_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            service = ChatService(
                StubAgent(),
                ConversationLogRepository(Path(temporary_directory)),
            )

            response = service.reply(ChatRequest(message="Tóm tắt Day 1"))

            self.assertIsNotNone(response.conversation_id)
            self.assertGreater(len(response.conversation_id or ""), 10)
            record = json.loads(
                next(Path(temporary_directory).glob("*.jsonl")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(record["conversation_id"], response.conversation_id)

    def test_agent_exception_is_logged_without_error_message(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            service = ChatService(
                FailingAgent(),
                ConversationLogRepository(Path(temporary_directory)),
            )

            with self.assertRaises(RuntimeError):
                service.reply(
                    ChatRequest(
                        message="Trigger failure",
                        conversation_id="failed-session",
                    )
                )

            record = json.loads(
                next(Path(temporary_directory).glob("*.jsonl")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertIsNone(record["response"])
            self.assertEqual(record["error"], {"type": "RuntimeError"})
            self.assertNotIn("synthetic failure", json.dumps(record))

    def test_logging_failure_does_not_break_chat_response(self) -> None:
        service = ChatService(StubAgent(), BrokenLogRepository())

        response = service.reply(
            ChatRequest(message="Vẫn phải trả lời", conversation_id="demo-02")
        )

        self.assertEqual(response.status, "answered")
        self.assertEqual(response.conversation_id, "demo-02")


if __name__ == "__main__":
    unittest.main()
