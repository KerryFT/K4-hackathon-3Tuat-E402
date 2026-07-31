import re

from app.schemas.chat import LearningContext


def resolve_scope(message: str, context: LearningContext) -> str:
    normalized = message.casefold()
    requested_days = set(re.findall(r"\b(?:day|bài)\s*0?(\d+)\b", normalized))

    # If explicit days are mentioned in the question (e.g., "Day 2", "bài 2", "Day 02")
    if requested_days:
        current_day_num = None
        if context.current_lecture_id:
            m = re.search(r"(\d+)", context.current_lecture_id)
            if m:
                current_day_num = str(int(m.group(1)))

        # If user asks about a different day or multiple days
        if len(requested_days) >= 2 or (current_day_num and any(str(int(d)) != current_day_num for d in requested_days)):
            return "selected_lectures"
        return "selected_lectures"

    if any(
        term in normalized
        for term in (
            "toàn khóa",
            "các bài khác",
            "tài liệu khác",
            "bài khác",
            "bài nào khác",
            "xuyên bài",
            "xuyên ngày",
            "tất cả bài",
            "khóa học",
        )
    ):
        return "all_lectures"

    if any(term in normalized for term in ("trang này", "slide này")) and context.current_page:
        return "current_page"

    if context.selected_lecture_ids:
        return "selected_lectures"

    # If asking for summary or general question without restricting to "slide này"
    if any(term in normalized for term in ("tóm tắt", "tom tat", "tất cả", "nội dung chính", "ý chính")):
        return "all_lectures"

    if context.current_lecture_id:
        return "current_lecture"

    return "all_lectures"
