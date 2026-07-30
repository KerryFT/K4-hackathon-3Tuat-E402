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
        if matches:
            ranked = sorted(matches, key=lambda item: item.score, reverse=True)
            if request.diversify_lectures:
                diverse: list[SourceChunk] = []
                seen_lectures: set[str] = set()
                for chunk in ranked:
                    if chunk.lecture_id not in seen_lectures:
                        diverse.append(chunk)
                        seen_lectures.add(chunk.lecture_id)
                selected_ids = {chunk.source_id for chunk in diverse}
                diverse.extend(
                    chunk for chunk in ranked if chunk.source_id not in selected_ids
                )
                ranked = diverse
            return ranked[: request.top_k]
        if request.allow_scope_fallback:
            return scoped[: request.top_k]
        return []
