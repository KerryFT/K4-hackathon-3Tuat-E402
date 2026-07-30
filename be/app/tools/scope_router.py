import re

from app.schemas.chat import LearningContext


def resolve_scope(message: str, context: LearningContext) -> str:
    normalized = message.casefold()
    requested_days = set(re.findall(r"\bday\s*0?(\d+)\b", normalized))
    if requested_days:
        return "selected_lectures"
    if any(
        term in normalized
        for term in (
            "toàn khóa",
            "các bài khác",
            "bài nào khác",
            "xuyên bài",
            "xuyên ngày",
        )
    ):
        return "all_lectures"
    if any(term in normalized for term in ("trang này", "slide này")) and context.current_page:
        return "current_page"
    if context.selected_lecture_ids:
        return "selected_lectures"
    if context.current_lecture_id:
        return "current_lecture"
    return "all_lectures"
