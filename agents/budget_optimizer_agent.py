"""Simple budget optimization logic."""

from typing import Dict, Any
from .openai_utils import generate_response


class BudgetOptimizerAgent:
    """Suggests a basic allocation for disposable income."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount = context.get("amount")

        prompt = (
            "You are a budgeting expert. Provide a short recommendation for how "
            "to allocate a user's disposable income. Include specific dollar "
            "amounts if provided. Limit to two sentences.\nContext: "
            f"{context}"
        )
        result = generate_response(prompt, max_tokens=80)

        return {
            "result": result,
            "confidence_score": 0.82,
            "metadata": {"context": context},
        }
