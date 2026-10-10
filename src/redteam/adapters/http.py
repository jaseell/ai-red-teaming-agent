from typing import Any

import httpx

from redteam.adapters.base import TargetAdapter, TargetResponse


class HTTPTargetAdapter(TargetAdapter):
    def __init__(
        self,
        *,
        endpoint: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.headers = headers or {}

    def send(self, prompt: str) -> TargetResponse:
        response = httpx.post(
            self.endpoint,
            json={"prompt": prompt},
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data: Any = response.json()
        content = self._extract_content(data)

        return TargetResponse(
            content=content,
            model=data.get("model") if isinstance(data, dict) else None,
            raw_response=data,
        )

    @staticmethod
    def _extract_content(data: Any) -> str:
        if not isinstance(data, dict):
            raise TypeError("Target response must be a JSON object.")

        content = data.get("content")

        if not isinstance(content, str):
            raise TypeError(
                "Target response must contain a string 'content' field."
            )

        return content
