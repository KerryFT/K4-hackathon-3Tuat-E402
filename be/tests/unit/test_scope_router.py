import unittest

from app.schemas.chat import LearningContext
from app.tools.scope_router import resolve_scope


class ScopeRouterTests(unittest.TestCase):
    def test_current_slide_uses_current_page(self) -> None:
        context = LearningContext(current_lecture_id="day-02", current_page=4)
        self.assertEqual(resolve_scope("Tóm tắt slide này", context), "current_page")

    def test_other_lecture_request_searches_all_lectures(self) -> None:
        context = LearningContext(current_lecture_id="day-02", current_page=4)
        self.assertEqual(
            resolve_scope("Khái niệm này có ở bài nào khác?", context),
            "all_lectures",
        )

    def test_two_explicit_days_use_selected_lectures(self) -> None:
        self.assertEqual(
            resolve_scope(
                "Liên hệ Day 1 và Day 2",
                LearningContext(),
            ),
            "selected_lectures",
        )


if __name__ == "__main__":
    unittest.main()
