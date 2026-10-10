from typing import Any

import httpx

from redteam.adapters.base import TargetAdapter, TargetResponse


class OllamaTargetAdapter(TargetAdapter):
    def __init__(
        self,
        *,
        model: str = "qwen2.5:3b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.endpoint = f"{base_url.rstrip('/')}/api/chat"
        self.timeout = timeout

    def send(self, prompt: str) -> TargetResponse:
        response = httpx.post(
            self.endpoint,
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        data: Any = response.json()
        content = self._extract_content(data)

        return TargetResponse(
            content=content,
            model=data.get("model", self.model),
            raw_response=data,
        )

    @staticmethod
    def _extract_content(data: Any) -> str:
        if not isinstance(data, dict):
            raise TypeError("Ollama response must be a JSON object.")

        message = data.get("message")
        if not isinstance(message, dict):
            raise TypeError(
                "Ollama response must contain a 'message' object."
            )

        content = message.get("content")
        if not isinstance(content, str):
            raise TypeError(
                "Ollama response must contain string message content."
            )

        return content
