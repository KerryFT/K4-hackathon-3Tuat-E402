import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = "VLearn Context Tutor"
    environment: str = os.getenv("APP_ENV", "development")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: str = field(
        default=os.getenv("OPENAI_API_KEY", ""),
        repr=False,
    )
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")
    openai_reasoning_effort: str = os.getenv("OPENAI_REASONING_EFFORT", "low")
    context_token_budget: int = int(os.getenv("CONTEXT_TOKEN_BUDGET", "6000"))
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    retrieval_min_score: float = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.1"))
    lecture_index_path: str = os.getenv(
        "LECTURE_INDEX_PATH",
        str(BACKEND_DIR / "data" / "indexes" / "lecture_chunks.jsonl"),
    )
    cors_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:3001",
            ).split(",")
            if origin.strip()
        ]
    )


settings = Settings()
