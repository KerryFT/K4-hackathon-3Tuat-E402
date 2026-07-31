import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.providers.llm.base import LLMProviderError
from app.providers.llm.openai import OpenAILLMProvider
from app.schemas.chat import GroundedGeneration


class FakeChatCompletions:
    def __init__(self, response_text: str = "Test completion response"):
        self.response_text = response_text
        self.last_kwargs = {}

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        message = SimpleNamespace(content=self.response_text)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


_DEFAULT_GROUNDED = GroundedGeneration(
    answer="Grounded answer from OpenAI",
    citation_source_ids=["day-01:1:0"],
    suggested_questions=["Question 1"],
)


class FakeBetaChatCompletions:
    def __init__(self, parsed_object: GroundedGeneration | None = _DEFAULT_GROUNDED):
        self.parsed_object = parsed_object
        self.last_kwargs = {}


    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        message = SimpleNamespace(parsed=self.parsed_object)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class OpenAILLMProviderTests(unittest.TestCase):
    def test_init_raises_without_api_key(self) -> None:
        with self.assertRaises(ValueError):
            OpenAILLMProvider(api_key="", model="gpt-4o")

    def test_generate_standard_chat_completion(self) -> None:
        provider = OpenAILLMProvider(api_key="test-key", model="gpt-4o")
        fake_chat = FakeChatCompletions("Standard text answer")
        provider.client = SimpleNamespace(
            chat=SimpleNamespace(completions=fake_chat)
        )

        result = provider.generate("System prompt", "User question")
        self.assertEqual(result, "Standard text answer")
        self.assertEqual(fake_chat.last_kwargs["model"], "gpt-4o")
        self.assertEqual(
            fake_chat.last_kwargs["messages"],
            [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User question"},
            ],
        )

    def test_generate_grounded_standard_beta_parse(self) -> None:
        provider = OpenAILLMProvider(api_key="test-key", model="gpt-4o-mini")
        fake_beta = FakeBetaChatCompletions()
        provider.client = SimpleNamespace(
            beta=SimpleNamespace(chat=SimpleNamespace(completions=fake_beta))
        )

        result = provider.generate_grounded("System prompt", "User question")
        self.assertIsInstance(result, GroundedGeneration)
        self.assertEqual(result.answer, "Grounded answer from OpenAI")
        self.assertEqual(fake_beta.last_kwargs["model"], "gpt-4o-mini")
        self.assertIs(fake_beta.last_kwargs["response_format"], GroundedGeneration)

    def test_reasoning_effort_passed_for_o_series_models(self) -> None:
        provider = OpenAILLMProvider(
            api_key="test-key", model="o3-mini", reasoning_effort="high"
        )
        fake_chat = FakeChatCompletions()
        provider.client = SimpleNamespace(
            chat=SimpleNamespace(completions=fake_chat)
        )

        provider.generate("System", "User")
        self.assertEqual(fake_chat.last_kwargs["reasoning_effort"], "high")

    def test_generate_raises_llm_provider_error_on_exception(self) -> None:
        provider = OpenAILLMProvider(api_key="test-key", model="gpt-4o")
        mock_chat = MagicMock()
        mock_chat.completions.create.side_effect = Exception("API connection error")
        provider.client = SimpleNamespace(chat=mock_chat)

        with self.assertRaises(LLMProviderError):
            provider.generate("System", "User")

    def test_generate_grounded_raises_llm_provider_error_on_empty(self) -> None:
        provider = OpenAILLMProvider(api_key="test-key", model="gpt-4o")
        fake_beta = FakeBetaChatCompletions(parsed_object=None)
        provider.client = SimpleNamespace(
            beta=SimpleNamespace(chat=SimpleNamespace(completions=fake_beta))
        )

        with self.assertRaises(LLMProviderError):
            provider.generate_grounded("System", "User")


if __name__ == "__main__":
    unittest.main()
