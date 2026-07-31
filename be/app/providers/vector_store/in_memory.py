import re

from app.retrieval.filters import is_in_scope
from app.schemas.retrieval import SearchRequest, SourceChunk


def _terms(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold(), flags=re.UNICODE))


class InMemoryVectorStore:
    """Lexical development fallback; production can replace this provider."""

    def __init__(self) -> None:
        self._chunks: list[SourceChunk] = []

    def add(self, chunks: list[SourceChunk]) -> None:
        self._chunks.extend(chunks)

    def search(self, request: SearchRequest) -> list[SourceChunk]:
        query_terms = _terms(request.query)
        matches: list[SourceChunk] = []
        scoped: list[SourceChunk] = []
        for chunk in self._chunks:
            if not is_in_scope(chunk, request):
                continue
            scoped.append(chunk)
            content_terms = _terms(chunk.content)
            score = len(query_terms & content_terms) / max(len(query_terms), 1)
            if score:
                matches.append(chunk.model_copy(update={"score": score}))

        if request.page is not None:
            page_matches = [c for c in scoped if c.page == request.page]
            if page_matches:
                for pm in page_matches:
                    if not any(m.source_id == pm.source_id for m in matches):
                        matches.append(pm.model_copy(update={"score": 0.5}))

        if matches:
            ranked = sorted(matches, key=lambda item: item.score, reverse=True)
            if request.diversify_lectures and request.lecture_ids:
                diverse: list[SourceChunk] = []
                for lec_id in request.lecture_ids:
                    lec_chunks = [c for c in ranked if c.lecture_id == lec_id]
                    if not lec_chunks and request.allow_scope_fallback:
                        lec_chunks = [c for c in scoped if c.lecture_id == lec_id]
                    diverse.extend(lec_chunks[:3])
                selected_ids = {c.source_id for c in diverse}
                for c in ranked:
                    if c.source_id not in selected_ids:
                        diverse.append(c)
                        selected_ids.add(c.source_id)
                ranked = diverse
            return ranked[: request.top_k]

        if request.allow_scope_fallback:
            if request.diversify_lectures:
                grouped: dict[str, list[SourceChunk]] = {}
                for chunk in scoped:
                    grouped.setdefault(chunk.lecture_id, []).append(chunk)
                diversified: list[SourceChunk] = []
                offset = 0
                while len(diversified) < request.top_k:
                    added = False
                    for lecture_chunks in grouped.values():
                        if offset < len(lecture_chunks):
                            diversified.append(lecture_chunks[offset])
                            added = True
                            if len(diversified) == request.top_k:
                                break
                    if not added:
                        break
                    offset += 1
                return diversified
            return scoped[: request.top_k]
        return []
