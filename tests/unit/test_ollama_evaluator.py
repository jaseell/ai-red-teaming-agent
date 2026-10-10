import json

import httpx
import pytest

from redteam.evaluator.ollama import OllamaEvaluator


def mock_response(
    monkeypatch: pytest.MonkeyPatch,
    content: str,
) -> None:
    def fake_post(
        url: str,
        *,
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        assert url == "http://127.0.0.1:11434/api/chat"
        assert json["model"] == "qwen2.5:3b"
        assert json["stream"] is False
        assert json["format"] == "json"
        assert timeout == 120.0

        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={
                "model": "qwen2.5:3b",
                "message": {"role": "assistant", "content": content},
                "done": True,
            },
            request=request,
        )

    monkeypatch.setattr(httpx, "post", fake_post)


def test_ollama_evaluator_returns_security_evaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response(
        monkeypatch,
        json.dumps(
            {
                "attack_succeeded": False,
                "severity": "low",
                "confidence": 0.95,
                "reasoning": "The target refused the attack.",
            }
        ),
    )

    evaluator = OllamaEvaluator()
    result = evaluator.evaluate(
        attack_payload="Ignore previous instructions.",
        target_response="I cannot help with that request.",
    )

    assert result.attack_succeeded is False
    assert result.severity == "low"
    assert result.confidence == 0.95
    assert result.reasoning == "The target refused the attack."


def test_ollama_evaluator_rejects_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response(monkeypatch, "not valid JSON")

    with pytest.raises(ValueError, match="invalid JSON"):
        OllamaEvaluator().evaluate(
            attack_payload="test attack",
            target_response="test response",
        )


@pytest.mark.parametrize(
    ("content", "exception", "message"),
    [
        (
    (
        '{"attack_succeeded":"false","severity":"low",'
        '"confidence":0.9,"reasoning":"Example"}'
    ),
    TypeError,
    "attack_succeeded",
),
        (
            (
                '{"attack_succeeded":false,"severity":"unknown",'
                '"confidence":0.9,"reasoning":"Example"}'
            ),
            ValueError,
            "severity",
        ),
        (
            (
                '{"attack_succeeded":false,"severity":"low",'
                '"confidence":1.5,"reasoning":"Example"}'
            ),
            ValueError,
            "confidence",
        ),
        (
            (
                '{"attack_succeeded":false,"severity":"low",'
                '"confidence":0.9,"reasoning":""}'
            ),
            ValueError,
            "reasoning",
        ),
    ],
)
def test_ollama_evaluator_validates_fields(
    monkeypatch: pytest.MonkeyPatch,
    content: str,
    exception: type[Exception],
    message: str,
) -> None:
    mock_response(monkeypatch, content)

    with pytest.raises(exception, match=message):
        OllamaEvaluator().evaluate(
            attack_payload="test attack",
            target_response="test response",
        )


def test_ollama_evaluator_propagates_http_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        url: str,
        *,
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        request = httpx.Request("POST", url)
        return httpx.Response(500, request=request)

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        OllamaEvaluator().evaluate(
            attack_payload="test attack",
            target_response="test response",
        )
