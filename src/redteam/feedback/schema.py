from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryFeedback:
    category: str
    total: int
    succeeded: int
    failed: int
    unscored: int
    success_rate: float | None
