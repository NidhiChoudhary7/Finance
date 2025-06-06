"""Simple logic for handling major life events."""

from typing import Dict, Any


class LifeEventAgent:
    """Processes life events found in the user input."""

    LIFE_EVENTS = [
        "vacation",
        "wedding",
        "baby",
        "house",
        "car",
        "moving",
        "retirement",
    ]

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Return a short plan for the detected life event."""

        user_input = state.get("input", "").lower()
        context = state.get("context", {}) or {}
        amount = context.get("amount")

        event = next((e for e in self.LIFE_EVENTS if e in user_input), None)

        if event:
            base = f"Plan created for upcoming {event}."
        else:
            base = "General life event plan created."

        if amount:
            base += f" Estimated budget: ${amount}."

        return {
            "result": base,
            "confidence_score": 0.85 if event else 0.6,
            "metadata": {"event": event, "amount": amount},
        }
