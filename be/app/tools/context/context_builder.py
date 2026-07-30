from app.schemas.retrieval import SourceChunk


def build_context(chunks: list[SourceChunk], character_budget: int = 18000) -> str:
    selected: list[str] = []
    used = 0
    for chunk in chunks:
        label = (
            f"[source_id={chunk.source_id} | "
            f"{chunk.lecture_title} | trang {chunk.page or '?'}]"
        )
        item = f"{label}\n{chunk.content}"
        if used + len(item) > character_budget:
            break
        selected.append(item)
        used += len(item)
    return "\n\n".join(selected)
