from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.citation import Citation


class LearningContext(BaseModel):
    course_id: str | None = None
    current_lecture_id: str | None = None
    current_page: int | None = None
    selected_lecture_ids: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None
    context: LearningContext = Field(default_factory=LearningContext)


class ChatResponse(BaseModel):
    answer: str
    status: Literal["answered", "needs_clarification", "not_grounded", "not_configured"]
    scope: str
    citations: list[Citation] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)


class GroundedGeneration(BaseModel):
    """Structured result produced by the LLM before server-side validation."""

    answer: str = Field(min_length=1)
    citation_source_ids: list[str] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list, max_length=3)
