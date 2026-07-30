from app.providers.llm.base import LLMProviderError
from app.schemas.chat import GroundedGeneration


class OpenAILLMProvider:
    """OpenAI Responses API provider with Pydantic structured output."""

    configured = True

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        reasoning_effort: str = "low",
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI provider requires the openai package. "
                "Run: pip install -r requirements.txt"
            ) from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.reasoning_effort = reasoning_effort

    def _generation_options(self) -> dict:
        options: dict = {"store": False}
        if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
            options["reasoning"] = {"effort": self.reasoning_effort}
        if self.model.startswith("gpt-5"):
            options["text"] = {"verbosity": "low"}
        return options

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                **self._generation_options(),
            )
        except Exception as exc:
            raise LLMProviderError("OpenAI generation failed") from exc
        if not response.output_text:
            raise LLMProviderError("OpenAI returned an empty text response")
        return response.output_text

    def generate_grounded(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> GroundedGeneration:
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                text_format=GroundedGeneration,
                **self._generation_options(),
            )
        except Exception as exc:
            raise LLMProviderError("OpenAI structured generation failed") from exc
        if response.output_parsed is None:
            raise LLMProviderError("OpenAI returned no structured result")
        return response.output_parsed
