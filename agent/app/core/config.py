from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]


def _resolve_repo_path(value: Path) -> Path:
    path = value.expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    agent_port: int = 8001
    openai_api_key: SecretStr | None = None
    openai_model: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    agent_data_root: Path = REPO_ROOT / "data" / "transcript"
    agent_chroma_dir: Path = REPO_ROOT / "agent" / ".cache" / "chroma"
    agent_summary_cache_dir: Path = (
        REPO_ROOT / "agent" / ".cache" / "summaries"
    )
    agent_chunk_size: int = Field(default=4000, ge=500, le=20000)
    agent_chunk_overlap: int = Field(default=400, ge=0, le=5000)
    agent_retrieval_top_k: int = Field(default=6, ge=1, le=20)
    agent_summary_batch_chars: int = Field(
        default=30000, ge=5000, le=100000
    )

    @field_validator(
        "agent_data_root",
        "agent_chroma_dir",
        "agent_summary_cache_dir",
        mode="before",
    )
    @classmethod
    def resolve_paths(cls, value: str | Path) -> Path:
        return _resolve_repo_path(Path(value))

    @field_validator("agent_chunk_overlap")
    @classmethod
    def validate_overlap(cls, value: int, info) -> int:
        chunk_size = info.data.get("agent_chunk_size", 4000)
        if value >= chunk_size:
            raise ValueError("AGENT_CHUNK_OVERLAP must be smaller than chunk size")
        return value

    @property
    def openai_configured(self) -> bool:
        key = self.openai_api_key
        return bool(
            key
            and key.get_secret_value().strip()
            and self.openai_model.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
