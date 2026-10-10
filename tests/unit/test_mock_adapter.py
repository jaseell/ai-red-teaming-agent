from redteam.adapters.base import TargetResponse
from redteam.adapters.mock import MockTargetAdapter


def test_mock_adapter_returns_target_response() -> None:
    adapter = MockTargetAdapter(
        response="Mock LLM response",
        model="test-model",
    )

    result = adapter.send("Hello test target")

    assert isinstance(result, TargetResponse)
    assert result.content == "Mock LLM response"
    assert result.model == "test-model"
    assert result.raw_response == {
        "prompt": "Hello test target",
        "content": "Mock LLM response",
    }
