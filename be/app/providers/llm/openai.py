import logging
import time

from app.providers.llm.base import LLMProviderError
from app.schemas.chat import GroundedGeneration

logger = logging.getLogger(__name__)


class OpenAILLMProvider:
    """OpenAI API provider with Pydantic structured output support."""

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
        options: dict = {}
        if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
            options["reasoning_effort"] = self.reasoning_effort
        return options

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        for attempt in range(4):
            try:
                if hasattr(self.client, "responses"):
                    options: dict = {"store": False}
                    if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
                        options["reasoning"] = {"effort": self.reasoning_effort}
                    if self.model.startswith("gpt-5"):
                        options["text"] = {"verbosity": "low"}
                    response = self.client.responses.create(
                        model=self.model,
                        instructions=system_prompt,
                        input=user_prompt,
                        **options,
                    )
                    output_text = getattr(response, "output_text", None)
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        **self._generation_options(),
                    )
                    output_text = (
                        response.choices[0].message.content
                        if response and response.choices
                        else None
                    )
                if output_text:
                    return output_text
            except Exception as exc:
                if "rate_limit" in str(exc).lower() and attempt < 3:
                    logger.warning("OpenAI RateLimit hit, backing off 6s...")
                    time.sleep(6.0)
                    continue
                raise LLMProviderError("OpenAI generation failed") from exc

        raise LLMProviderError("OpenAI returned an empty text response")

    def generate_grounded(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> GroundedGeneration:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        for attempt in range(4):
            try:
                if hasattr(self.client, "responses"):
                    options: dict = {"store": False}
                    if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
                        options["reasoning"] = {"effort": self.reasoning_effort}
                    if self.model.startswith("gpt-5"):
                        options["text"] = {"verbosity": "low"}
                    response = self.client.responses.parse(
                        model=self.model,
                        instructions=system_prompt,
                        input=user_prompt,
                        text_format=GroundedGeneration,
                        **options,
                    )
                    parsed = getattr(response, "output_parsed", None)
                else:
                    response = self.client.beta.chat.completions.parse(
                        model=self.model,
                        messages=messages,
                        response_format=GroundedGeneration,
                        **self._generation_options(),
                    )
                    parsed = (
                        response.choices[0].message.parsed
                        if response and response.choices
                        else None
                    )
                if parsed is not None:
                    return parsed
            except Exception as exc:
                if "rate_limit" in str(exc).lower() and attempt < 3:
                    logger.warning("OpenAI RateLimit hit, backing off 6s...")
                    time.sleep(6.0)
                    continue
                raise LLMProviderError("OpenAI structured generation failed") from exc

        raise LLMProviderError("OpenAI returned no structured result")
