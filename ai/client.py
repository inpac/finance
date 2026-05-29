import anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_claude(system_prompt: str, user_message: str, model: str = DEFAULT_MODEL) -> tuple[str, dict]:
    client = get_client()
    response = client.messages.create(
        model=model,
        max_tokens=3000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "cache_read": getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_write": getattr(response.usage, "cache_creation_input_tokens", 0),
    }
    return response.content[0].text, usage
