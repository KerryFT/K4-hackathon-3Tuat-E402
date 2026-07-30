import unittest
from pathlib import Path

from app.providers.vector_store.jsonl import JsonlVectorStore
from app.retrieval.chunker import chunk_text, normalize_text
from app.schemas.retrieval import SearchRequest, SourceChunk
from scripts.ingest_documents import infer_lecture


class ChunkerTests(unittest.TestCase):
    def test_normalize_text_removes_pdf_spacing_noise(self) -> None:
        self.assertEqual(
            normalize_text("  First   line \r\n\r\n Second\tline\x00 "),
            "First line\n\nSecond line",
        )

    def test_oversized_paragraph_is_split_with_stable_ids(self) -> None:
        chunks = chunk_text(
            "word " * 80,
            course_id="course",
            lecture_id="day-01",
            lecture_title="Day 1",
            page=3,
            max_characters=100,
        )
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk.content) <= 100 for chunk in chunks))
        self.assertEqual(chunks[0].source_id, "day-01:3:0")
        self.assertEqual(chunks[-1].source_id, f"day-01:3:{len(chunks) - 1}")


class LectureMetadataTests(unittest.TestCase):
    def test_infer_lecture_from_hackathon_filename(self) -> None:
        self.assertEqual(
            infer_lecture(Path("d2-slide-hackathon.pdf")),
            ("day-02", "Day 2"),
        )


class JsonlVectorStoreTests(unittest.TestCase):
    def test_index_can_be_reloaded_and_searched_with_scope(self) -> None:
        chunks = [
            SourceChunk(
                source_id="day-01:1:0",
                course_id="course",
                lecture_id="day-01",
                lecture_title="Day 1",
                page=1,
                content="Problem statement and customer evidence",
            ),
            SourceChunk(
                source_id="day-02:4:0",
                course_id="course",
                lecture_id="day-02",
                lecture_title="Day 2",
                page=4,
                content="Prototype evaluation and golden set",
            ),
        ]
        index_path = Path("tests") / ".test-lecture-chunks.jsonl"
        temporary_path = index_path.with_suffix(f"{index_path.suffix}.tmp")
        try:
            JsonlVectorStore(index_path).replace(chunks)
            reloaded = JsonlVectorStore(index_path)
            results = reloaded.search(
                SearchRequest(
                    query="golden set",
                    scope="selected_lectures",
                    lecture_ids=["day-02"],
                )
            )
        finally:
            index_path.unlink(missing_ok=True)
            temporary_path.unlink(missing_ok=True)

        self.assertEqual([result.source_id for result in results], ["day-02:4:0"])
        self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
