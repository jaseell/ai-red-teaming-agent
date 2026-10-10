import httpx
import pytest

from redteam.adapters.http import HTTPTargetAdapter


def test_http_adapter_returns_target_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict[str, str],
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        assert url == "http://localhost:8000/generate"
        assert json == {"prompt": "test prompt"}
        assert headers == {}
        assert timeout == 30.0

        request = httpx.Request("POST", url)

        return httpx.Response(
            status_code=200,
            json={
                "content": "Test response",
                "model": "test-model",
            },
            request=request,
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    adapter = HTTPTargetAdapter(
        endpoint="http://localhost:8000/generate",
    )

    result = adapter.send("test prompt")

    assert result.content == "Test response"
    assert result.model == "test-model"
    assert result.raw_response == {
        "content": "Test response",
        "model": "test-model",
    }


def test_http_adapter_raises_for_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict[str, str],
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        request = httpx.Request("POST", url)

        return httpx.Response(
            status_code=500,
            json={"error": "internal server error"},
            request=request,
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    adapter = HTTPTargetAdapter(
        endpoint="http://localhost:8000/generate",
    )

    with pytest.raises(httpx.HTTPStatusError):
        adapter.send("test prompt")


def test_http_adapter_rejects_invalid_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_post(
        url: str,
        *,
        json: dict[str, str],
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        request = httpx.Request("POST", url)

        return httpx.Response(
            status_code=200,
            json={"model": "test-model"},
            request=request,
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    adapter = HTTPTargetAdapter(
        endpoint="http://localhost:8000/generate",
    )

    with pytest.raises(TypeError):
        adapter.send("test prompt")
