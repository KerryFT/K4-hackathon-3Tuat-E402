"""Build the local lecture search index from slide PDFs and transcript Markdown files."""

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


DEFAULT_VLEARN_PACK_DIR = BACKEND_DIR / "vlearn-pack"
DEFAULT_SLIDES_DIR = (
    DEFAULT_VLEARN_PACK_DIR / "slides"
    if (DEFAULT_VLEARN_PACK_DIR / "slides").exists()
    else REPO_DIR / "fe" / "public" / "slides"
)
DEFAULT_TRANSCRIPTS_DIR = DEFAULT_VLEARN_PACK_DIR / "transcript"
DEFAULT_INDEX_PATH = BACKEND_DIR / "data" / "indexes" / "lecture_chunks.jsonl"


def infer_lecture(path: Path) -> tuple[str, str]:
    match = re.search(r"(?:^|[-_])d(?:ay)?[-_]?(\d+)", path.stem, re.IGNORECASE)
    if not match:
        return "day-01", f"Tài liệu {path.stem}"
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
                lecture_title=f"{lecture_title} Slide",
                page=page.page,
                max_characters=max_characters,
            )
        )
    return chunks, len(pages)


def ingest_transcript_md(
    path: Path,
    *,
    course_id: str,
) -> list[SourceChunk]:
    text = path.read_text(encoding="utf-8")
    chunks: list[SourceChunk] = []

    # Map transcript to lecture_id
    if any(name in path.name for name in ("01", "02", "03")):
        lecture_id = "day-02"
        lecture_title = "Day 2 Transcript"
    elif any(name in path.name for name in ("04", "06")):
        lecture_id = "day-01"
        lecture_title = "Day 1 Transcript"
    else:
        lecture_id = "day-01"
        lecture_title = "Transcript Bài Giảng"

    current_section = None
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        para_strip = para.strip()
        if not para_strip:
            continue
        if para_strip.startswith("## "):
            current_section = para_strip.lstrip("#").strip()
            continue
        if para_strip.startswith("# "):
            continue

        tag_match = re.search(r"\*\*\[(T\d+-\d+)\]\*\*\s*(.*)", para_strip, re.DOTALL)
        if tag_match:
            tag = tag_match.group(1)
            content = tag_match.group(2).strip()
            chunks.append(
                SourceChunk(
                    source_id=tag,
                    course_id=course_id,
                    lecture_id=lecture_id,
                    lecture_title=lecture_title,
                    section=current_section,
                    content=content,
                )
            )
        elif len(para_strip) > 50 and not para_strip.startswith(">"):
            chunk_id = f"{path.stem}:{len(chunks)}"
            chunks.append(
                SourceChunk(
                    source_id=chunk_id,
                    course_id=course_id,
                    lecture_id=lecture_id,
                    lecture_title=lecture_title,
                    section=current_section,
                    content=para_strip,
                )
            )
    return chunks


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract slide PDFs and transcripts to build a persistent JSONL search index."
    )
    parser.add_argument("--slides-dir", type=Path, default=DEFAULT_SLIDES_DIR)
    parser.add_argument("--transcripts-dir", type=Path, default=DEFAULT_TRANSCRIPTS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--course-id", default="comp2010-phase-1")
    parser.add_argument("--max-characters", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_chunks: list[SourceChunk] = []
    sources: list[dict[str, object]] = []

    # 1. Ingest Slide PDFs
    if args.slides_dir.exists():
        pdf_paths = sorted(args.slides_dir.glob("*.pdf"))
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
                    "type": "pdf",
                    "lecture_id": lecture_id,
                    "lecture_title": lecture_title,
                    "sha256": file_sha256(path),
                    "pages_with_text": extracted_pages,
                    "chunks": len(chunks),
                }
            )
            print(f"PDF {path.name}: {extracted_pages} pages with text, {len(chunks)} chunks")

    # 2. Ingest Transcript Markdown files
    if args.transcripts_dir.exists():
        md_paths = sorted(args.transcripts_dir.glob("*.md"))
        for path in md_paths:
            if path.name.lower() == "readme.md":
                continue
            chunks = ingest_transcript_md(
                path,
                course_id=args.course_id,
            )
            all_chunks.extend(chunks)
            sources.append(
                {
                    "file": path.name,
                    "type": "transcript_md",
                    "sha256": file_sha256(path),
                    "chunks": len(chunks),
                }
            )
            print(f"Transcript {path.name}: {len(chunks)} chunks ingested")

    if not all_chunks:
        raise SystemExit("No PDF or Transcript files found to ingest!")

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
    print(f"\nSUCCESS: Wrote {len(all_chunks)} total chunks to {args.output}")
    print(f"Wrote manifest to {manifest_path}")


if __name__ == "__main__":
    main()
