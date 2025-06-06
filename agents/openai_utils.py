import os
import openai


def generate_response(prompt: str) -> str:
    """Return a short completion from OpenAI if a key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[OpenAI API key not set] " + prompt
    try:
        client = openai.OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"
