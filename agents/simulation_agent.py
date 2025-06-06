"""Simple scenario simulation logic."""

from typing import Dict, Any


class SimulationAgent:
    """Runs a basic simulation of financial scenarios."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        params = state.get("simulation_params", {}) or {}
        context = state.get("context", {}) or {}
        timeframe = context.get("timeframe")

        scenario = params.get("scenario_type", "generic")

        if scenario == "job_loss":
            desc = "Simulated six months of income loss"
        elif scenario == "emergency":
            desc = "Simulated emergency expense impact"
        elif scenario == "market_downturn":
            desc = "Simulated market downturn effect on portfolio"
        else:
            desc = "Simulated generic scenario"

        if timeframe:
            desc += f" over {timeframe[0]} {timeframe[1]}s"

        return {
            "result": desc,
            "confidence_score": 0.78,
            "metadata": {"scenario": scenario, "timeframe": timeframe},
        }
