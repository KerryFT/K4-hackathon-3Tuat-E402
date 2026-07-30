from app.schemas.chat import GroundedGeneration


class MockLLMProvider:
    configured = False

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "Mock provider: configure a real LLM before grounded generation."

    def generate_grounded(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> GroundedGeneration:
        return GroundedGeneration(answer=self.generate(system_prompt, user_prompt))
