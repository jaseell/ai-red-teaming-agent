
from redteam.feedback.service import FeedbackService
from redteam.generator.base import AttackGenerator
from redteam.generator.service import AttackPersistenceService
from redteam.models.attack import Attack


class FeedbackGuidedGenerationService:
    """Generate attacks using historical feedback and persist them."""

    def __init__(
        self,
        *,
        generator: AttackGenerator,
        feedback_service: FeedbackService,
        persistence_service: AttackPersistenceService,
    ) -> None:
        self.generator = generator
        self.feedback_service = feedback_service
        self.persistence_service = persistence_service

    def generate_and_persist(
        self,
        *,
        category: str,
        target_context: str,
        count: int = 1,
    ) -> list[Attack]:
        if count < 1:
            raise ValueError("count must be at least 1")

        feedback = self.feedback_service.summarize_by_category()

        generated_attacks = self.generator.generate(
            category=category,
            target_context=target_context,
            count=count,
            feedback=feedback,
        )

        return [
            self.persistence_service.persist(generated_attack)
            for generated_attack in generated_attacks
        ]
