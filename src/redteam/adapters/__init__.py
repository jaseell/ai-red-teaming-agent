from redteam.adapters.base import TargetAdapter, TargetResponse
from redteam.adapters.http import HTTPTargetAdapter
from redteam.adapters.mock import MockTargetAdapter
from redteam.adapters.ollama import OllamaTargetAdapter

__all__ = [
    "HTTPTargetAdapter",
    "MockTargetAdapter",
    "OllamaTargetAdapter",
    "TargetAdapter",
    "TargetResponse",
]
