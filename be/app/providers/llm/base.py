from typing import Protocol

from app.schemas.chat import GroundedGeneration


class LLMProvider(Protocol):
    configured: bool

    def generate(self, system_prompt: str, user_prompt: str) -> str: ...

    def generate_grounded(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> GroundedGeneration: ...


class LLMProviderError(RuntimeError):
    """Raised when generation fails or returns no structured result."""
