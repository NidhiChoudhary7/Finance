import os
import json
import openai


def generate_response(prompt: str, max_tokens: int = 60) -> str:
    """Return a completion from OpenAI if a key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[OpenAI API key not set] " + prompt
    try:
        client = openai.OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"


def generate_json(prompt: str, max_tokens: int = 200) -> dict:
    """Return a JSON dict parsed from an OpenAI completion."""
    text = generate_response(prompt, max_tokens=max_tokens)
    try:
        return json.loads(text)
    except Exception:
        return {}


def summarize_results(results: list[str], max_tokens: int = 120) -> str:
    """Combine multiple responses into one coherent summary."""
    joined = "\n".join(f"- {r}" for r in results if r)
    prompt = (
        "Summarize the following financial recommendations into a single, "
        f"clear response:\n{joined}"
    )
    return generate_response(prompt, max_tokens=max_tokens)
