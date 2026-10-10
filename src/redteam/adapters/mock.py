from redteam.adapters.base import TargetAdapter, TargetResponse


class MockTargetAdapter(TargetAdapter):
    def __init__(
        self,
        *,
        response: str = "Mock target response",
        model: str = "mock-model",
    ) -> None:
        self.response = response
        self.model = model

    def send(self, prompt: str) -> TargetResponse:
        return TargetResponse(
            content=self.response,
            model=self.model,
            raw_response={
                "prompt": prompt,
                "content": self.response,
            },
        )
