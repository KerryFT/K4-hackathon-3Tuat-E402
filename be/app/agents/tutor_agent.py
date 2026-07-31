import logging
import re
from pathlib import Path

from app.core.config import BACKEND_DIR, Settings, settings
from app.providers.llm.base import LLMProvider, LLMProviderError
from app.providers.llm.factory import create_llm_provider
from app.providers.vector_store.jsonl import JsonlVectorStore
from app.retrieval.hybrid_search import HybridSearch
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.citation import Citation
from app.schemas.retrieval import SearchRequest, SourceChunk
from app.tools.context.context_builder import build_context
from app.tools.guardrails.academic_integrity import requests_impersonation_or_cheating
from app.tools.guardrails.detect_out_of_scope import (
    is_dangerous_or_illegal,
    is_off_topic_query,
    is_prompt_injection_or_trick,
)
from app.tools.scope_router import resolve_scope
from app.tools.validation.citation_validator import validate_citations
from app.tools.validation.validate_grounding import validate_grounding


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là VLearn AI Tutor - Trợ lý học tập chuyên môn cao cấp cho khóa học VLearn.

QUY TẮC PHẢN HỒI VÀ TÓM TẮT THÔNG MINH (DỄ HIỂU, ĐẦY ĐỦ VÀ TRÌNH BÀY ĐẸP MẮT):

1. TÓM TẮT DỄ HIỂU & ĐẦY ĐỦ Ý:
   - Trình bày câu trả lời rõ ràng, mạch lạc, diễn giải chi tiết và DỄ HIỂU cho người đọc.
   - KHÔNG TRẢ LỜI QUÁ NGẮN hoặc quá sơ sài. Phải giải thích đầy đủ bản chất, bối cảnh và ý nghĩa của từng khái niệm.
   - Cấu trúc bài trả lời gồm:
     + Lời mở đầu súc tích dẫn dắt vấn đề.
     + Các gạch đầu dòng phân tích đầy đủ các luận điểm/ý chính.
     + Lời kết luận hoặc tổng kết ngắn gọn.

2. ĐỊNH DẠNG TRÌNH BÀY THẨM MỸ (BẮT BUỘC):
   - Trình bày dạng gạch đầu dòng `- ` cho từng ý chính trên một dòng mới.
   - Giữa các phần hoặc tiêu đề chính PHẢI có dòng trống để người đọc không bị rối mắt.
   - Dùng in đậm `**từ khóa quan trọng**` để làm nổi bật các khái niệm thuật ngữ.

3. VĂN PHONG HỌC THUẬT & TRÍCH DẪN NGUỒN:
   - Ngôn ngữ học thuật chuẩn mực, diễn đạt giàu hình ảnh sư phạm, gần gũi và dễ tiếp thu.
   - Chỉ dùng dữ liệu từ <SOURCE_CONTEXT> và đính kèm citation_source_id hợp lệ.
   - Đề xuất 2-3 câu hỏi ôn tập đào sâu mở rộng."""


class TutorAgent:
    """Coordinates scope, retrieval, generation and citation validation."""

    def __init__(
        self,
        *,
        search_engine: HybridSearch | None,
        llm: LLMProvider,
        top_k: int = 5,
        min_score: float = 0.1,
        context_character_budget: int = 18000,
    ) -> None:
        self.search_engine = search_engine
        self.llm = llm
        self.top_k = top_k
        self.min_score = min_score
        self.context_character_budget = context_character_budget

    def _get_search_engine(self) -> HybridSearch | None:
        if self.search_engine is not None:
            return self.search_engine
        index_path = BACKEND_DIR / "data" / "indexes" / "lecture_chunks.jsonl"
        if index_path.exists():
            self.search_engine = HybridSearch(JsonlVectorStore(index_path))
            return self.search_engine
        return None

    @staticmethod
    def _is_greeting(message: str) -> bool:
        normalized = message.casefold().strip()
        greetings = ("xin chào", "chào bạn", "hello", "hi", "chào ai tutor", "chào vlearn", "bạn là ai")
        return normalized in greetings or any(normalized == g for g in greetings)

    def run(self, request: ChatRequest) -> ChatResponse:
        scope = resolve_scope(request.message, request.context)

        if is_dangerous_or_illegal(request.message):
            return ChatResponse(
                answer=(
                    "Yêu cầu của bạn không nằm trong phạm vi nội dung học tập an toàn. "
                    "VLearn AI Tutor chỉ hỗ trợ giải đáp các kiến thức chuyên môn có trong tài liệu slide bài giảng VLearn."
                ),
                status="out_of_scope",
                scope=scope,
                suggested_questions=[
                    "Tóm tắt bài giảng Day 1",
                    "Problem statement là gì?",
                    "Gợi ý câu hỏi ôn tập",
                ],
            )

        if is_prompt_injection_or_trick(request.message):
            return ChatResponse(
                answer=(
                    "VLearn AI Tutor được thiết kế để hỗ trợ học tập và giải đáp nội dung môn học. "
                    "Vui lòng đặt câu hỏi liên quan đến nội dung tài liệu slide bài giảng VLearn."
                ),
                status="out_of_scope",
                scope=scope,
                suggested_questions=[
                    "Tóm tắt bài giảng Day 1",
                    "Problem statement là gì?",
                    "Giải thích khái niệm trong slide",
                ],
            )

        if self._is_greeting(request.message):
            return ChatResponse(
                answer=(
                    "Xin chào! Tôi là VLearn AI Tutor - Trợ lý học tập chuyên môn cho khóa học. "
                    "Tôi có thể hỗ trợ bạn tóm tắt nội dung slide bài giảng, giải thích các khái niệm học thuật và gợi ý câu hỏi ôn tập. "
                    "Bạn cần tìm hiểu hoặc giải đáp nội dung bài học nào hôm nay?"
                ),
                status="answered",
                scope=scope,
                suggested_questions=[
                    "Tóm tắt bài giảng Day 1",
                    "Problem statement là gì?",
                    "So sánh nội dung Day 1 và Day 2",
                ],
            )

        clarification = self._clarification_response(request, scope)
        if clarification:
            return clarification

        if is_off_topic_query(request.message):
            return ChatResponse(
                answer=(
                    "Câu hỏi của bạn không thuộc phạm vi tài liệu môn học VLearn. "
                    "VLearn AI Tutor chỉ hỗ trợ giải đáp các vấn đề liên quan đến slide bài giảng (Day 1, Day 2) và kiến thức học tập liên quan."
                ),
                status="out_of_scope",
                scope=scope,
                suggested_questions=[
                    "Tóm tắt bài giảng Day 1",
                    "Problem statement là gì?",
                    "Gợi ý câu hỏi ôn tập",
                ],
            )

        if requests_impersonation_or_cheating(request.message):
            return ChatResponse(
                answer=(
                    "Tôi không thể làm bài tập hoặc hoàn thành yêu cầu thay bạn. "
                    "Tuy nhiên, tôi có thể giải thích lý thuyết liên quan và hướng dẫn các bước thực hiện dựa trên tài liệu bài giảng để hỗ trợ bạn."
                ),
                status="not_grounded",
                scope=scope,
                suggested_questions=[
                    "Giải thích khái niệm liên quan trong slide",
                    "Gợi ý định hướng các bước thực hiện",
                ],
            )

        search_engine = self._get_search_engine()
        if search_engine is None:
            return self._not_configured(
                scope,
                "Kho slide chưa được lập chỉ mục. Hãy chạy pipeline ingest trước.",
            )

        allow_scope_fallback = self._is_summary_request(request.message)
        search_request = self._build_search_request(
            request,
            scope,
            allow_scope_fallback=allow_scope_fallback,
        )
        sources = search_engine.search(search_request)
        if not allow_scope_fallback:
            sources = [source for source in sources if source.score >= self.min_score]

        if not sources and scope in {"current_lecture", "current_page"}:
            fallback_request = self._build_search_request(
                request,
                "all_lectures",
                allow_scope_fallback=allow_scope_fallback,
            )
            fallback_sources = search_engine.search(fallback_request)
            if not allow_scope_fallback:
                fallback_sources = [s for s in fallback_sources if s.score >= self.min_score]
            sources = fallback_sources

        if not sources:
            return ChatResponse(
                answer=(
                    "Nội dung bạn tìm kiếm hiện chưa có trong tài liệu slide bài giảng VLearn được cung cấp. "
                    "Vui lòng kiểm tra lại câu hỏi hoặc chọn đúng tài liệu bài giảng (Day 1 / Day 2) để tôi tra cứu chính xác."
                ),
                status="not_grounded",
                scope=scope,
                suggested_questions=[
                    "Tìm trong tất cả bài giảng",
                    "Hỏi về nội dung Day 1 và Day 2",
                ],
            )

        if not self.llm.configured:
            return self._not_configured(
                scope,
                "Đã tìm thấy nguồn nhưng LLM thật chưa được cấu hình.",
            )

        source_context = build_context(
            sources,
            character_budget=self.context_character_budget,
        )
        user_prompt = (
            "<SOURCE_CONTEXT>\n"
            f"{source_context}\n"
            "</SOURCE_CONTEXT>\n\n"
            f"<QUESTION>{request.message}</QUESTION>"
        )
        try:
            generation = self.llm.generate_grounded(SYSTEM_PROMPT, user_prompt)
        except LLMProviderError:
            logger.exception("Grounded generation failed")
            return ChatResponse(
                answer=(
                    "Hệ thống chưa thể khởi tạo câu trả lời từ nguồn trích dẫn ở lượt này. "
                    "Vui lòng thử lại sau."
                ),
                status="not_grounded",
                scope=scope,
            )

        citations = self._citations_from_ids(
            generation.citation_source_ids,
            sources,
        )
        if not (
            validate_citations(citations, sources)
            and validate_grounding(True, citations)
            and len(citations) == len(set(generation.citation_source_ids))
            and self._citations_cover_requested_lectures(citations, search_request)
        ):
            logger.warning(
                "Blocked answer with invalid citations: %s",
                generation.citation_source_ids,
            )
            return ChatResponse(
                answer=(
                    "Phản hồi không xác minh được nguồn trích dẫn hợp lệ từ tài liệu slide. "
                    "Câu trả lời bị chặn nhằm bảo đảm tính chính xác của dữ liệu học thuật."
                ),
                status="not_grounded",
                scope=scope,
            )

        return ChatResponse(
            answer=generation.answer,
            status="answered",
            scope=scope,
            citations=citations,
            suggested_questions=generation.suggested_questions,
        )

    def _clarification_response(
        self,
        request: ChatRequest,
        scope: str,
    ) -> ChatResponse | None:
        normalized = request.message.casefold()
        refers_to_current_page = any(
            phrase in normalized for phrase in ("slide này", "trang này")
        )
        if refers_to_current_page and (
            request.context.current_page is None
            or request.context.current_lecture_id is None
        ):
            return ChatResponse(
                answer=(
                    "Bạn muốn hỏi trang nào? Hãy mở slide cần hỏi hoặc chọn rõ "
                    "Day và số trang để mình dùng đúng nguồn."
                ),
                status="needs_clarification",
                scope=scope,
            )
        return None

    def _build_search_request(
        self,
        request: ChatRequest,
        scope: str,
        *,
        allow_scope_fallback: bool,
    ) -> SearchRequest:
        lecture_ids: list[str] = []
        if scope in {"current_page", "current_lecture"}:
            if request.context.current_lecture_id:
                lecture_ids = [request.context.current_lecture_id]
        elif scope == "selected_lectures":
            lecture_ids = (
                request.context.selected_lecture_ids
                or self._extract_lecture_ids(request.message)
            )

        return SearchRequest(
            query=request.message,
            scope=scope,
            course_id=request.context.course_id,
            lecture_ids=lecture_ids,
            page=request.context.current_page if scope == "current_page" else None,
            top_k=self.top_k,
            allow_scope_fallback=allow_scope_fallback,
            diversify_lectures=len(lecture_ids) > 1,
        )

    @staticmethod
    def _is_summary_request(message: str) -> bool:
        normalized = message.casefold()
        return any(
            term in normalized
            for term in ("tóm tắt", "tom tat", "ý chính", "nội dung chính")
        )

    @staticmethod
    def _extract_lecture_ids(message: str) -> list[str]:
        days = {
            int(day)
            for day in re.findall(r"\bday\s*0?(\d+)\b", message.casefold())
        }
        return [f"day-{day:02d}" for day in sorted(days)]

    @staticmethod
    def _citations_cover_requested_lectures(
        citations: list[Citation],
        search_request: SearchRequest,
    ) -> bool:
        if (
            search_request.scope != "selected_lectures"
            or len(search_request.lecture_ids) < 2
        ):
            return True
        cited_lectures = {citation.lecture_id for citation in citations}
        return set(search_request.lecture_ids).issubset(cited_lectures)

    @staticmethod
    def _citations_from_ids(
        source_ids: list[str],
        sources: list[SourceChunk],
    ) -> list[Citation]:
        source_by_id = {source.source_id: source for source in sources}
        citations: list[Citation] = []
        seen: set[str] = set()
        for source_id in source_ids:
            if source_id in seen:
                continue
            seen.add(source_id)
            source = source_by_id.get(source_id)
            if source is None:
                continue
            citations.append(
                Citation(
                    source_id=source.source_id,
                    lecture_id=source.lecture_id,
                    lecture_title=source.lecture_title,
                    page=source.page,
                    excerpt=source.content[:240],
                )
            )
        return citations

    @staticmethod
    def _not_configured(scope: str, reason: str) -> ChatResponse:
        return ChatResponse(
            answer=reason,
            status="not_configured",
            scope=scope,
            suggested_questions=[
                "Tóm tắt bài giảng hiện tại",
                "Liên hệ kiến thức Day 1 và Day 2",
            ],
        )


def build_tutor_agent(config: Settings = settings) -> TutorAgent:
    index_path = Path(config.lecture_index_path)
    if not index_path.is_absolute():
        index_path = BACKEND_DIR / index_path
    search_engine = (
        HybridSearch(JsonlVectorStore(index_path)) if index_path.exists() else None
    )
    return TutorAgent(
        search_engine=search_engine,
        llm=create_llm_provider(config),
        top_k=config.retrieval_top_k,
        min_score=config.retrieval_min_score,
        context_character_budget=config.context_token_budget * 3,
    )


tutor_agent = build_tutor_agent()
