from dataclasses import dataclass
from pathlib import Path

from app.retrieval.chunker import normalize_text


@dataclass(frozen=True)
class ExtractedPage:
    page: int
    content: str


def extract_pdf_pages(path: Path) -> list[ExtractedPage]:
    """Extract non-empty pages from a PDF, using one-based page numbers."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF extraction requires pypdf. Run: pip install -r requirements.txt"
        ) from exc

    reader = PdfReader(str(path))
    pages: list[ExtractedPage] = []
    for page_number, pdf_page in enumerate(reader.pages, start=1):
        content = normalize_text(pdf_page.extract_text() or "")
        if content:
            pages.append(ExtractedPage(page=page_number, content=content))
    return pages
