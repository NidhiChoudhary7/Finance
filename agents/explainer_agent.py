"""Converts technical results into simple language."""

from typing import Dict, Any
from .openai_utils import generate_response


class ExplainerAgent:
    """Provides user-friendly explanations of agent results."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        final_result = state.get("final_result", "")

        if final_result:
            prompt = (
                "Explain the following in very simple language in one sentence:\n"
                f"{final_result}"
            )
            explanation = generate_response(prompt, max_tokens=60)
        else:
            explanation = "Unable to generate an explanation."

        return {
            "explanation": explanation,
            "confidence_score": 0.80,
            "metadata": {},
        }
