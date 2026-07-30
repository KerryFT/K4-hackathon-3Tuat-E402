from app.core.config import Settings
from app.core.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.mock import MockLLMProvider
from app.providers.llm.openai import OpenAILLMProvider


def create_llm_provider(config: Settings = settings) -> LLMProvider:
    if config.llm_provider == "mock":
        return MockLLMProvider()
    if config.llm_provider == "openai":
        if not config.openai_api_key:
            return MockLLMProvider()
        return OpenAILLMProvider(
            api_key=config.openai_api_key,
            model=config.openai_model,
            reasoning_effort=config.openai_reasoning_effort,
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {config.llm_provider}")
