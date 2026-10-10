import httpx
import pytest

from redteam.adapters.ollama import OllamaTargetAdapter


def test_ollama_adapter_returns_target_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        assert url == "http://127.0.0.1:11434/api/chat"
        assert json["model"] == "qwen2.5:3b"
        assert json["messages"] == [
            {"role": "user", "content": "test prompt"}
        ]
        assert json["stream"] is False
        assert timeout == 120.0

        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={
                "model": "qwen2.5:3b",
                "message": {
                    "role": "assistant",
                    "content": '{"status":"ok"}',
                },
                "done": True,
            },
            request=request,
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = OllamaTargetAdapter().send("test prompt")

    assert result.content == '{"status":"ok"}'
    assert result.model == "qwen2.5:3b"
    assert result.raw_response["done"] is True


def test_ollama_adapter_raises_for_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        request = httpx.Request("POST", url)
        return httpx.Response(500, json={"error": "failed"}, request=request)

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(httpx.HTTPStatusError):
        OllamaTargetAdapter().send("test prompt")


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"message": None},
        {"message": {"content": None}},
    ],
)
def test_ollama_adapter_rejects_invalid_response(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        request = httpx.Request("POST", url)
        return httpx.Response(200, json=payload, request=request)

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(TypeError):
        OllamaTargetAdapter().send("test prompt")
