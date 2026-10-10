from sqlalchemy.orm import Session

from redteam.generator.base import GeneratedAttack
from redteam.models.attack import Attack
from redteam.repositories.attack import AttackRepository


class AttackPersistenceService:
    def __init__(self, db_session: Session) -> None:
        self.repository = AttackRepository(db_session)

    def persist(self, generated_attack: GeneratedAttack) -> Attack:
        return self.repository.create(
            name=generated_attack.name,
            category=generated_attack.category,
            description=generated_attack.description,
            payload=generated_attack.payload,
            severity=generated_attack.severity,
        )
