from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal


ControlIntent = Literal["small_talk", "prompt_injection"]


@dataclass(frozen=True)
class ControlRoute:
    intent: ControlIntent
    answer: str
    suggested_questions: list[str]


def _normalize(message: str) -> str:
    value = unicodedata.normalize("NFD", message.casefold())
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


_SMALL_TALK_PATTERNS = (
    re.compile(
        r"^(?:(?:xin\s+)?chao|hello|hi|hey|alo|good\s+(?:morning|afternoon|evening))"
        r"(?:\s+(?:ban|thay|co|tutor|tro\s+ly|vlearn))*$"
    ),
    re.compile(r"^(?:cam\s+on|thanks|thank\s+you)(?:\s+(?:ban|tutor|vlearn))*$"),
    re.compile(r"^(?:tam\s+biet|bye|goodbye|hen\s+gap\s+lai)$"),
    re.compile(r"^(?:ban\s+la\s+ai|ban\s+lam\s+duoc\s+gi)$"),
)


_INJECTION_PATTERNS = (
    re.compile(
        r"\b(?:bo\s+qua|phot\s+lo|quen|ignore|disregard|override)\b.{0,60}"
        r"\b(?:chi\s+dan|huong\s+dan|prompt|instruction|system|developer|quy\s+tac)"
    ),
    re.compile(
        r"\b(?:tiet\s+lo|hien\s+thi|in\s+ra|doc\s+lai|show|reveal|print|repeat)\b.{0,60}"
        r"\b(?:system\s+prompt|developer\s+message|hidden\s+instruction|prompt\s+he\s+thong|"
        r"chi\s+dan\s+an|api\s+key|secret)"
    ),
    re.compile(
        r"\b(?:you\s+are\s+now|act\s+as|gia\s+vo\s+la|dong\s+vai)\b.{0,60}"
        r"\b(?:dan|jailbreak|khong\s+bi\s+rang\s+buoc|unrestricted|developer|system)"
    ),
    re.compile(r"\b(?:jailbreak|developer\s+mode|do\s+anything\s+now)\b"),
    re.compile(r"(?:<\s*/?\s*(?:source_context|question|system)\s*>|\[\s*inst\s*\])"),
)


def route_control_message(message: str) -> ControlRoute | None:
    """Handle messages that must not enter retrieval or model generation.

    This is intentionally deterministic. It protects the expensive RAG path and
    avoids asking the model to decide whether it should obey an attack directed
    at that same model.
    """

    normalized = _normalize(message)
    if any(pattern.fullmatch(normalized) for pattern in _SMALL_TALK_PATTERNS):
        if re.fullmatch(r"(?:cam\s+on|thanks|thank\s+you).*", normalized):
            answer = "Không có gì! Mình sẵn sàng giúp bạn học và tra cứu nội dung trong slide."
        elif re.fullmatch(r"(?:tam\s+biet|bye|goodbye|hen\s+gap\s+lai)", normalized):
            answer = "Tạm biệt bạn! Khi cần ôn bài hoặc kiểm tra nội dung slide, cứ quay lại nhé."
        elif normalized in {"ban la ai", "ban lam duoc gi"}:
            answer = (
                "Mình là trợ giảng VLearn. Mình có thể giải thích, tóm tắt và liên hệ "
                "kiến thức trong các slide Day 1–Day 2, kèm nguồn theo trang."
            )
        else:
            answer = (
                "Xin chào! Mình là trợ giảng VLearn. Bạn muốn tóm tắt slide, "
                "giải thích khái niệm hay liên hệ kiến thức giữa các Day?"
            )
        return ControlRoute(
            intent="small_talk",
            answer=answer,
            suggested_questions=[
                "Tóm tắt bài giảng hiện tại",
                "Giải thích một khái niệm trong slide",
                "Liên hệ kiến thức Day 1 và Day 2",
            ],
        )

    if any(pattern.search(normalized) for pattern in _INJECTION_PATTERNS):
        return ControlRoute(
            intent="prompt_injection",
            answer=(
                "Mình không thể làm theo yêu cầu thay đổi hoặc tiết lộ chỉ dẫn hệ thống. "
                "Mình vẫn có thể giúp bạn với nội dung học tập trong slide Day 1–Day 2."
            ),
            suggested_questions=[
                "Giải thích prompt injection theo nội dung slide",
                "Tóm tắt bài giảng hiện tại",
            ],
        )
    return None
