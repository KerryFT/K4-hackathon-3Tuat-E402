import re

from app.schemas.retrieval import SourceChunk


def normalize_text(text: str) -> str:
    """Normalize PDF text while keeping paragraph boundaries."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    normalized: list[str] = []
    for line in lines:
        if line:
            normalized.append(line)
        elif normalized and normalized[-1] != "":
            normalized.append("")
    return "\n".join(normalized).strip()


def _split_oversized(text: str, max_characters: int) -> list[str]:
    """Split a long PDF text block without dropping any words."""
    if len(text) <= max_characters:
        return [text]

    pieces: list[str] = []
    remaining = text
    while len(remaining) > max_characters:
        boundary = max(
            remaining.rfind(". ", 0, max_characters + 1),
            remaining.rfind("; ", 0, max_characters + 1),
            remaining.rfind(" ", 0, max_characters + 1),
        )
        if boundary < max_characters // 2:
            boundary = max_characters
        elif remaining[boundary : boundary + 2] in {". ", "; "}:
            boundary += 1
        pieces.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    if remaining:
        pieces.append(remaining)
    return pieces


def chunk_text(
    text: str,
    *,
    course_id: str,
    lecture_id: str,
    lecture_title: str,
    page: int | None = None,
    max_characters: int = 1200,
) -> list[SourceChunk]:
    """Create deterministic, page-scoped chunks from extracted slide text."""
    if max_characters < 100:
        raise ValueError("max_characters must be at least 100")

    text = normalize_text(text)
    paragraphs = [
        piece
        for part in text.split("\n\n")
        if part.strip()
        for piece in _split_oversized(part.strip(), max_characters)
    ]
    chunks: list[SourceChunk] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip()
        if buffer and len(candidate) > max_characters:
            chunks.append(
                SourceChunk(
                    source_id=f"{lecture_id}:{page or 0}:{len(chunks)}",
                    course_id=course_id,
                    lecture_id=lecture_id,
                    lecture_title=lecture_title,
                    page=page,
                    content=buffer,
                )
            )
            buffer = paragraph
        else:
            buffer = candidate
    if buffer:
        chunks.append(
            SourceChunk(
                source_id=f"{lecture_id}:{page or 0}:{len(chunks)}",
                course_id=course_id,
                lecture_id=lecture_id,
                lecture_title=lecture_title,
                page=page,
                content=buffer,
            )
        )
    return chunks
