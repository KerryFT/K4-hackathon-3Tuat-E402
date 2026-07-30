from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


DayId = Literal["day_1", "day_2"]
RunMode = Literal["summary", "qa"]


class AgentRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_id: DayId
    mode: RunMode
    query: str | None = Field(default=None, max_length=8000)

    @model_validator(mode="after")
    def validate_query(self) -> "AgentRunRequest":
        if self.mode == "qa":
            if self.query is None or not self.query.strip():
                raise ValueError("query is required when mode='qa'")
            self.query = self.query.strip()
        elif self.query is not None:
            self.query = None
        return self


class Citation(BaseModel):
    source: str
    heading: str | None = None
    segment_ids: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    day_id: DayId
    mode: RunMode
    answer: str
    citations: list[Citation] = Field(default_factory=list)
