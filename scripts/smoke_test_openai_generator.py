from redteam.core.config import get_settings
from redteam.generator.openai import OpenAIAttackGenerator


def main() -> None:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    generator = OpenAIAttackGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )

    attacks = generator.generate(
        category="prompt_injection",
        target_context=(
            "An authorized local test chatbot that should follow its "
            "system instructions and refuse attempts to override them."
        ),
        count=2,
    )

    print(f"Generated {len(attacks)} attack(s):")

    for index, attack in enumerate(attacks, start=1):
        print(f"\nAttack {index}")
        print(f"Name: {attack.name}")
        print(f"Category: {attack.category}")
        print(f"Severity: {attack.severity}")
        print(f"Description: {attack.description}")
        print(f"Payload: {attack.payload}")


if __name__ == "__main__":
    main()
