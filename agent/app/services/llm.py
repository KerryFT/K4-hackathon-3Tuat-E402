from __future__ import annotations

from typing import Protocol

from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import Settings
from app.core.errors import ModelConfigurationError


class ModelProvider(Protocol):
    async def complete(self, system_prompt: str, user_prompt: str) -> str: ...

    def embeddings(self) -> Embeddings: ...


class OpenAIModelProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._chat_model: ChatOpenAI | None = None
        self._embeddings: OpenAIEmbeddings | None = None

    def _credentials(self) -> tuple[str, str]:
        key = self.settings.openai_api_key
        api_key = key.get_secret_value().strip() if key else ""
        model = self.settings.openai_model.strip()
        if not api_key or not model:
            raise ModelConfigurationError(
                "OPENAI_API_KEY and OPENAI_MODEL must be configured"
            )
        return api_key, model

    def chat_model(self) -> ChatOpenAI:
        if self._chat_model is None:
            api_key, model = self._credentials()
            self._chat_model = ChatOpenAI(
                api_key=api_key,
                model=model,
            )
        return self._chat_model

    def embeddings(self) -> Embeddings:
        if self._embeddings is None:
            api_key, _ = self._credentials()
            self._embeddings = OpenAIEmbeddings(
                api_key=api_key,
                model=self.settings.openai_embedding_model,
            )
        return self._embeddings

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        message = await self.chat_model().ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        if isinstance(message.content, str):
            return message.content.strip()
        text_parts = [
            str(block.get("text", ""))
            for block in message.content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(text_parts).strip()
