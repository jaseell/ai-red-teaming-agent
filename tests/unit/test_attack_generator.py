import pytest

from redteam.generator import MockAttackGenerator


def test_mock_attack_generator_generates_matching_attacks():
    generator = MockAttackGenerator()

    attacks = generator.generate(
        category="prompt_injection",
        target_context="A test chatbot with instruction-following behavior.",
        count=2,
    )

    assert len(attacks) == 2

    assert attacks[0].category == "prompt_injection"
    assert attacks[0].name == "Direct Instruction Override"

    assert attacks[1].category == "prompt_injection"
    assert attacks[1].name == "Role Confusion"


def test_mock_attack_generator_returns_empty_for_unknown_category():
    generator = MockAttackGenerator()

    attacks = generator.generate(
        category="unknown_category",
        target_context="Test target",
    )

    assert attacks == []


def test_mock_attack_generator_rejects_invalid_count():
    generator = MockAttackGenerator()

    with pytest.raises(ValueError, match="count must be at least 1"):
        generator.generate(
            category="prompt_injection",
            target_context="Test target",
            count=0,
        )
