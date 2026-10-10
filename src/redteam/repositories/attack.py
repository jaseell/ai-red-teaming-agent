from sqlalchemy import select
from sqlalchemy.orm import Session

from redteam.models.attack import Attack


class AttackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        name: str,
        category: str,
        payload: str,
        severity: str,
        description: str | None = None,
    ) -> Attack:
        attack = Attack(
            name=name,
            category=category,
            payload=payload,
            severity=severity,
            description=description,
        )

        self.db.add(attack)
        self.db.flush()
        self.db.refresh(attack)

        return attack

    def get_by_id(self, attack_id: int) -> Attack | None:
        statement = select(Attack).where(Attack.id == attack_id)
        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Attack | None:
        statement = select(Attack).where(Attack.name == name)
        return self.db.scalar(statement)

    def list_active(self) -> list[Attack]:
        statement = (
            select(Attack)
            .where(Attack.is_active.is_(True))
            .order_by(Attack.id)
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        attack: Attack,
        *,
        name: str | None = None,
        category: str | None = None,
        payload: str | None = None,
        severity: str | None = None,
        description: str | None = None,
    ) -> Attack:
        if name is not None:
            attack.name = name

        if category is not None:
            attack.category = category

        if payload is not None:
            attack.payload = payload

        if severity is not None:
            attack.severity = severity

        if description is not None:
            attack.description = description

        self.db.flush()
        self.db.refresh(attack)

        return attack

    def deactivate(self, attack: Attack) -> Attack:
        attack.is_active = False

        self.db.flush()
        self.db.refresh(attack)

        return attack
