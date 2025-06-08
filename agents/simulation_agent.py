"""Simple scenario simulation logic."""

from typing import Dict, Any
from .openai_utils import generate_response


class SimulationAgent:
    """Runs a basic simulation of financial scenarios."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        params = state.get("simulation_params", {}) or {}
        context = state.get("context", {}) or {}
        timeframe = context.get("timeframe")

        scenario = params.get("scenario_type", "generic")

        prompt = (
            "Briefly describe the financial impact of a "
            f"{scenario} scenario. If a timeframe is provided include it.\n"
            f"Timeframe: {timeframe}"
        )
        desc = generate_response(prompt, max_tokens=80)

        return {
            "result": desc,
            "confidence_score": 0.78,
            "metadata": {"scenario": scenario, "timeframe": timeframe},
        }
