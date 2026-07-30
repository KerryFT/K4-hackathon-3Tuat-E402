from __future__ import annotations

from app.core.config import Settings, get_settings
from app.graph import build_graph
from app.services.documents import TranscriptLoader
from app.services.index import TranscriptIndexManager
from app.services.llm import ModelProvider, OpenAIModelProvider
from app.tools.transcripts import TranscriptTools


class AgentRuntime:
    def __init__(
        self,
        settings: Settings | None = None,
        model_provider: ModelProvider | None = None,
        index_manager: TranscriptIndexManager | None = None,
    ):
        self.settings = settings or get_settings()
        self.loader = TranscriptLoader(self.settings)
        self.model_provider = model_provider or OpenAIModelProvider(self.settings)
        self.index_manager = index_manager or TranscriptIndexManager(
            settings=self.settings,
            loader=self.loader,
            embedding_factory=self.model_provider.embeddings,
        )
        self.tools = TranscriptTools(
            settings=self.settings,
            loader=self.loader,
            index_manager=self.index_manager,
            model_provider=self.model_provider,
        )
        self.graph = build_graph(self.tools)


def create_runtime(settings: Settings | None = None) -> AgentRuntime:
    return AgentRuntime(settings=settings)
