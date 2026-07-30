"""Build the local lecture search index from slide PDFs."""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.providers.vector_store.jsonl import JsonlVectorStore
from app.retrieval.chunker import chunk_text
from app.retrieval.pdf_extractor import extract_pdf_pages
from app.schemas.retrieval import SourceChunk


DEFAULT_SLIDES_DIR = REPO_DIR / "fe" / "public" / "slides"
DEFAULT_INDEX_PATH = BACKEND_DIR / "data" / "indexes" / "lecture_chunks.jsonl"


def infer_lecture(path: Path) -> tuple[str, str]:
    match = re.search(r"(?:^|[-_])d(?:ay)?[-_]?(\d+)", path.stem, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"Cannot infer lecture day from '{path.name}'. "
            "Use a filename such as d1-slides.pdf or day-02.pdf."
        )
    day = int(match.group(1))
    return f"day-{day:02d}", f"Day {day}"


def ingest_pdf(
    path: Path,
    *,
    course_id: str,
    max_characters: int,
) -> tuple[list[SourceChunk], int]:
    lecture_id, lecture_title = infer_lecture(path)
    pages = extract_pdf_pages(path)
    chunks: list[SourceChunk] = []
    for page in pages:
        chunks.extend(
            chunk_text(
                page.content,
                course_id=course_id,
                lecture_id=lecture_id,
                lecture_title=lecture_title,
                page=page.page,
                max_characters=max_characters,
            )
        )
    return chunks, len(pages)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract slide PDFs and build a persistent JSONL search index."
    )
    parser.add_argument("--slides-dir", type=Path, default=DEFAULT_SLIDES_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--course-id", default="comp2010-phase-1")
    parser.add_argument("--max-characters", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pdf_paths = sorted(args.slides_dir.glob("*.pdf"))
    if not pdf_paths:
        raise SystemExit(f"No PDF files found in {args.slides_dir}")

    all_chunks: list[SourceChunk] = []
    sources: list[dict[str, object]] = []
    for path in pdf_paths:
        chunks, extracted_pages = ingest_pdf(
            path,
            course_id=args.course_id,
            max_characters=args.max_characters,
        )
        all_chunks.extend(chunks)
        lecture_id, lecture_title = infer_lecture(path)
        sources.append(
            {
                "file": path.name,
                "lecture_id": lecture_id,
                "lecture_title": lecture_title,
                "sha256": file_sha256(path),
                "pages_with_text": extracted_pages,
                "chunks": len(chunks),
            }
        )
        print(f"{path.name}: {extracted_pages} pages with text, {len(chunks)} chunks")

    store = JsonlVectorStore(args.output)
    store.replace(all_chunks)
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "course_id": args.course_id,
        "max_characters": args.max_characters,
        "chunk_count": len(all_chunks),
        "sources": sources,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(all_chunks)} chunks to {args.output}")
    print(f"Wrote manifest to {manifest_path}")


if __name__ == "__main__":
    main()
