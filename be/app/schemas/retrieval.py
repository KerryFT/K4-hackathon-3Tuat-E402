from typing import Literal

from pydantic import BaseModel, Field


SearchScope = Literal[
    "current_page",
    "current_lecture",
    "selected_lectures",
    "all_lectures",
]


class SearchRequest(BaseModel):
    query: str
    scope: SearchScope
    course_id: str | None = None
    lecture_ids: list[str] = Field(default_factory=list)
    page: int | None = None
    top_k: int = 5
    allow_scope_fallback: bool = False
    diversify_lectures: bool = False


class SourceChunk(BaseModel):
    source_id: str
    course_id: str
    lecture_id: str
    lecture_title: str
    page: int | None = None
    section: str | None = None
    content: str
    score: float = 0.0
