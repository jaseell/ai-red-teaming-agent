from sqlalchemy import select
from sqlalchemy.orm import Session

from redteam.models.target import Target


class TargetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        name: str,
        target_type: str,
        endpoint: str | None = None,
        description: str | None = None,
    ) -> Target:
        target = Target(
            name=name,
            target_type=target_type,
            endpoint=endpoint,
            description=description,
        )

        self.db.add(target)
        self.db.flush()
        self.db.refresh(target)

        return target

    def get_by_id(self, target_id: int) -> Target | None:
        statement = select(Target).where(Target.id == target_id)
        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Target | None:
        statement = select(Target).where(Target.name == name)
        return self.db.scalar(statement)

    def list_active(self) -> list[Target]:
        statement = (
            select(Target)
            .where(Target.is_active.is_(True))
            .order_by(Target.id)
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        target: Target,
        *,
        name: str | None = None,
        target_type: str | None = None,
        endpoint: str | None = None,
        description: str | None = None,
    ) -> Target:
        if name is not None:
            target.name = name

        if target_type is not None:
            target.target_type = target_type

        if endpoint is not None:
            target.endpoint = endpoint

        if description is not None:
            target.description = description

        self.db.flush()
        self.db.refresh(target)

        return target

    def deactivate(self, target: Target) -> Target:
        target.is_active = False

        self.db.flush()
        self.db.refresh(target)

        return target
