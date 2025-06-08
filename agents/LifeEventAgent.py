"""Simple logic for handling major life events."""

from typing import Dict, Any
from .openai_utils import generate_response


class LifeEventAgent:
    """Processes life events found in the user input."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Return a short plan for the detected life event."""

        user_input = state.get("input", "")
        context = state.get("context", {}) or {}

        prompt = (
            "You are a helpful financial assistant. Provide a concise plan or "
            "set of tips for the following user request. If a specific life "
            "event is mentioned, tailor the advice accordingly. Limit the "
            "response to no more than three sentences.\nRequest: "
            f"{user_input}\nContext: {context}"
        )
        result = generate_response(prompt, max_tokens=100)

        return {
            "result": result,
            "confidence_score": 0.85,
            "metadata": {"context": context},
        }
