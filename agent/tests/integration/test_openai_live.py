import os

import pytest

from app.runtime import create_runtime


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_INTEGRATION") != "1",
    reason="Set RUN_OPENAI_INTEGRATION=1 to run live OpenAI tests",
)
@pytest.mark.asyncio
async def test_live_day_1_question_is_grounded():
    runtime = create_runtime()
    result = await runtime.graph.ainvoke(
        {
            "day_id": "day_1",
            "mode": "qa",
            "query": "Attention trong transformer là gì?",
        }
    )
    assert result["answer"]
    assert result["citations"]
    assert all(
        citation["source"].startswith(("transcript-04", "transcript-05", "transcript-06"))
        for citation in result["citations"]
    )
