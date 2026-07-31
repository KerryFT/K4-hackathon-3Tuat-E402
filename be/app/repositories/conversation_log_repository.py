import hashlib
import json
import threading
from pathlib import Path
from typing import Any


class ConversationLogRepository:
    """Append-only JSONL storage for local conversation audit events."""

    def __init__(self, directory: Path, *, enabled: bool = True) -> None:
        self.directory = directory
        self.enabled = enabled
        self._write_lock = threading.Lock()

    def append(self, event: dict[str, Any]) -> None:
        if not self.enabled:
            return

        conversation_id = str(event["conversation_id"])
        payload = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        path = self._path_for(conversation_id)

        with self._write_lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.write("\n")
                handle.flush()

    def _path_for(self, conversation_id: str) -> Path:
        digest = hashlib.sha256(conversation_id.encode("utf-8")).hexdigest()
        return self.directory / f"{digest}.jsonl"
