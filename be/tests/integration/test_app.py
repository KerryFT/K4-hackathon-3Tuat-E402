import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.conversation_log_repository import ConversationLogRepository
from app.schemas.chat import ChatResponse
from app.services.chat_service import chat_service


class StubAgent:
    def run(self, request) -> ChatResponse:
        return ChatResponse(
            answer="Grounded answer",
            status="answered",
            scope="all_lectures",
        )


class AppStructureTests(unittest.TestCase):
    def test_required_routes_are_registered(self) -> None:
        # FastAPI may keep included routers lazy; OpenAPI is the stable public view.
        paths = set(app.openapi()["paths"])
        self.assertIn("/api/course/info", paths)
        self.assertIn("/api/v1/health", paths)
        self.assertIn("/api/v1/chat", paths)

    def test_chat_endpoint_delegates_to_agent_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            original_agent = chat_service.agent
            original_log_repository = chat_service.log_repository
            chat_service.agent = StubAgent()
            chat_service.log_repository = ConversationLogRepository(
                Path(temporary_directory),
            )
            try:
                response = TestClient(app).post(
                    "/api/v1/chat",
                    json={"message": "Problem statement là gì?"},
                )
            finally:
                chat_service.agent = original_agent
                chat_service.log_repository = original_log_repository

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "answered")
            self.assertEqual(response.json()["answer"], "Grounded answer")
            self.assertTrue(response.json()["conversation_id"])

            log_file = next(Path(temporary_directory).glob("*.jsonl"))
            record = json.loads(log_file.read_text(encoding="utf-8"))
            self.assertEqual(
                record["conversation_id"],
                response.json()["conversation_id"],
            )
            self.assertEqual(record["response"]["answer"], "Grounded answer")


if __name__ == "__main__":
    unittest.main()
