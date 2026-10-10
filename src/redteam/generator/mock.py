
from redteam.attack_library.definitions import ATTACK_DEFINITIONS
from redteam.feedback.schema import CategoryFeedback
from redteam.generator.base import AttackGenerator, GeneratedAttack


class MockAttackGenerator(AttackGenerator):
    def generate(
        self,
        *,
        category: str,
        target_context: str,
        count: int = 1,
        feedback: list[CategoryFeedback] | None = None,
    ) -> list[GeneratedAttack]:
        if count < 1:
            raise ValueError("count must be at least 1")

        matching_definitions = [
            definition
            for definition in ATTACK_DEFINITIONS
            if definition.category == category
        ]

        if not matching_definitions:
            return []

        selected_definitions = matching_definitions[:count]

        return [
            GeneratedAttack(
                name=definition.name,
                category=definition.category,
                description=definition.description,
                payload=definition.payload,
                severity=definition.severity,
            )
            for definition in selected_definitions
        ]

