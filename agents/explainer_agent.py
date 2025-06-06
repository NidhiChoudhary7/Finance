"""Converts technical results into simple language."""

from typing import Dict, Any


class ExplainerAgent:
    """Provides user-friendly explanations of agent results."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        final_result = state.get("final_result", "")

        if final_result:
            explanation = (
                "In short, " + final_result.replace("Simulated", "we simulated")
            )
        else:
            explanation = "Unable to generate an explanation."

        return {
            "explanation": explanation,
            "confidence_score": 0.80,
            "metadata": {},
        }
