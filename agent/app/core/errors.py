class AgentError(Exception):
    """Base class for expected agent failures."""

    code = "AGENT_ERROR"


class InvalidAgentRequest(AgentError):
    code = "INVALID_REQUEST"


class TranscriptDataError(AgentError):
    code = "TRANSCRIPT_DATA_UNAVAILABLE"


class ModelConfigurationError(AgentError):
    code = "MODEL_NOT_CONFIGURED"


class IndexBuildError(AgentError):
    code = "INDEX_BUILD_FAILED"
