
import argparse

from redteam.adapters.mock import MockTargetAdapter
from redteam.core.session import SessionLocal
from redteam.evaluator.base import Evaluator, SecurityEvaluation
from redteam.executor.service import AttackExecutionService
from redteam.reporting.security_summary import (
    write_security_summary_report,
)
from redteam.repositories.attack import AttackRepository
from redteam.repositories.target import TargetRepository


class MockEvaluator(Evaluator):
    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        return SecurityEvaluation(
            attack_succeeded=False,
            severity="low",
            confidence=0.95,
            reasoning="Mock evaluation: attack was not successful.",
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a controlled mock attack execution."
    )
    parser.add_argument(
        "--attack",
        default="Direct Instruction Override",
        help="Name of an existing seeded attack",
    )
    args = parser.parse_args()

    with SessionLocal() as db_session:
        attack_repository = AttackRepository(db_session)
        target_repository = TargetRepository(db_session)

        attack = attack_repository.get_by_name(args.attack)
        if attack is None:
            parser.error(
                f"Attack '{args.attack}' not found. "
                "Run the attack library seed command first."
            )

        target = target_repository.get_by_name(
            "Local Mock Test Target"
        )
        if target is None:
            target = target_repository.create(
                name="Local Mock Test Target",
                target_type="llm",
                endpoint="mock://local-test",
                description="Controlled target used for mock execution.",
            )
            db_session.flush()

        service = AttackExecutionService(
            db_session=db_session,
            adapter=MockTargetAdapter(),
            evaluator=MockEvaluator(),
        )

        result = service.execute(attack=attack, target=target)
        db_session.commit()

        report_path = write_security_summary_report(db_session)

        print("Mock execution completed.")
        print(f"Attack: {attack.name}")
        print(f"Target: {target.name}")
        print(f"Attack ID: {result.attack_id}")
        print("Evaluation: attack not successful (mock evaluator)")
        print(f"Security summary: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
