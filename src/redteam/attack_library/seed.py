from sqlalchemy.orm import Session

from redteam.attack_library.definitions import ATTACK_DEFINITIONS
from redteam.core.session import SessionLocal
from redteam.repositories.attack import AttackRepository


def seed_attacks(db_session: Session) -> int:
    repository = AttackRepository(db_session)
    created_count = 0

    for definition in ATTACK_DEFINITIONS:
        existing_attack = repository.get_by_name(definition.name)

        if existing_attack is not None:
            continue

        repository.create(
            name=definition.name,
            category=definition.category,
            description=definition.description,
            payload=definition.payload,
            severity=definition.severity,
        )

        created_count += 1

    db_session.commit()

    return created_count


def main() -> None:
    with SessionLocal() as db_session:
        created_count = seed_attacks(db_session)

    print(f"Seeded {created_count} new attacks.")


if __name__ == "__main__":
    main()
