from redteam.adapters.ollama import OllamaTargetAdapter


def main() -> None:
    adapter = OllamaTargetAdapter(model="qwen2.5:3b")

    response = adapter.send(
        'Reply with valid JSON only: '
        '{"status":"ok","purpose":"local red-team testing"}'
    )

    print(f"Model: {response.model}")
    print(f"Response: {response.content}")

    if not response.content.strip():
        raise RuntimeError("Ollama returned an empty response.")

    print("Ollama adapter smoke test passed.")


if __name__ == "__main__":
    main()
