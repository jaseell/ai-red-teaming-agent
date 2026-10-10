import pytest
from pydantic import ValidationError

from redteam.generator.schema import (
    GeneratedAttackResponse,
    GeneratedAttackSchema,
)


def test_generated_attack_schema_accepts_valid_attack():
    attack = GeneratedAttackSchema(
        name="Instruction Override",
        category="prompt_injection",
        description="Tests instruction boundary handling.",
        payload="Ignore previous instructions.",
        severity="medium",
    )

    assert attack.name == "Instruction Override"
    assert attack.category == "prompt_injection"
    assert attack.severity == "medium"


def test_generated_attack_response_accepts_multiple_attacks():
    response = GeneratedAttackResponse(
        attacks=[
            {
                "name": "Attack One",
                "category": "prompt_injection",
                "description": "First test attack.",
                "payload": "Test payload one.",
                "severity": "low",
            },
            {
                "name": "Attack Two",
                "category": "prompt_extraction",
                "description": "Second test attack.",
                "payload": "Test payload two.",
                "severity": "high",
            },
        ]
    )

    assert len(response.attacks) == 2
    assert response.attacks[0].name == "Attack One"
    assert response.attacks[1].severity == "high"


@pytest.mark.parametrize(
    "severity",
    ["info", "moderate", "urgent", "unknown"],
)
def test_generated_attack_schema_rejects_invalid_severity(severity):
    with pytest.raises(ValidationError):
        GeneratedAttackSchema(
            name="Invalid Severity Attack",
            category="prompt_injection",
            description="Invalid severity test.",
            payload="Test payload.",
            severity=severity,
        )


def test_generated_attack_schema_rejects_empty_payload():
    with pytest.raises(ValidationError):
        GeneratedAttackSchema(
            name="Empty Payload Attack",
            category="prompt_injection",
            description="Tests payload validation.",
            payload="",
            severity="medium",
        )


def test_generated_attack_response_rejects_empty_attack_list():
    with pytest.raises(ValidationError):
        GeneratedAttackResponse(attacks=[])
