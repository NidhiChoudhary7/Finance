# agents/planner.py
from typing import Dict, Any, List
import re

from dotenv import load_dotenv
load_dotenv(override=True)

class PlannerAgent:
    def __init__(self):
        self.query_patterns = {
            "life_event": [
                r"vacation|wedding|baby|house|car|moving|retirement",
                r"life event|major purchase|milestone"
            ],
            "budget_optimization": [
                r"bonus|raise|windfall|extra money|optimize|budget",
                r"allocate|distribute|spend|save"
            ],
            "investment_analysis": [
                r"portfolio|stocks|bonds|investment|market|returns",
                r"performance|analysis|recommendation"
            ],
            "simulation": [
                r"what if|scenario|simulate|predict|forecast",
                r"job loss|career change|emergency"
            ]
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes query and determines routing strategy"""
        user_input = state.get("input", "").lower()
        
        # Determine query type
        query_type = self._classify_query(user_input)
        
        # Extract context and parameters
        context = self._extract_context(user_input, query_type)
        
        # Determine if explanation is needed
        requires_explanation = self._needs_explanation(user_input)
        
        # Extract simulation parameters if applicable
        simulation_params = None
        if query_type == "simulation":
            simulation_params = self._extract_simulation_params(user_input)
        
        return {
            "query_type": query_type,
            "context": context,
            "requires_explanation": requires_explanation,
            "simulation_params": simulation_params
        }
    
    def _classify_query(self, user_input: str) -> str:
        """Classifies the user query into appropriate category"""
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return query_type
        
        return "general"
    
    def _extract_context(self, user_input: str, query_type: str) -> Dict[str, Any]:
        """Extracts relevant context from the user input"""
        context = {"requires_multiple_agents": False}
        
        # Check for monetary amounts
        # Updated regex to capture values like "$5000" by allowing more digits
        money_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        money_matches = re.findall(money_pattern, user_input)
        if money_matches:
            context["amount"] = money_matches[0].replace(",", "")
        
        # Check for time references
        time_pattern = r'(\d+)\s*(month|year|week|day)s?'
        time_matches = re.findall(time_pattern, user_input, re.IGNORECASE)
        if time_matches:
            context["timeframe"] = time_matches[0]

        # Risk tolerance
        if re.search(r"low risk|conservative|cautious", user_input, re.IGNORECASE):
            context["risk_tolerance"] = "low"
        elif re.search(r"medium risk|moderate", user_input, re.IGNORECASE):
            context["risk_tolerance"] = "medium"
        elif re.search(r"high risk|aggressive", user_input, re.IGNORECASE):
            context["risk_tolerance"] = "high"

        # Investment goals
        if re.search(r"retire|retirement", user_input, re.IGNORECASE):
            context["goal"] = "retirement"
        elif re.search(r"house|home|down payment", user_input, re.IGNORECASE):
            context["goal"] = "buy_home"
        elif re.search(r"emergency fund|rainy day|safety net", user_input, re.IGNORECASE):
            context["goal"] = "emergency_fund"

        # ESG preference
        if re.search(r"esg|ethical|sustainable|socially responsible|green", user_input, re.IGNORECASE):
            context["esg"] = True

        # Include holdings or expenses based on keywords
        if re.search(r"holdings|portfolio|existing investments", user_input, re.IGNORECASE):
            context["include_holdings"] = True
        if re.search(r"expenses|recurring bills|fixed costs", user_input, re.IGNORECASE):
            context["include_expenses"] = True

        # Simple overrides for common expenses
        overrides = {}
        for name in ["rent", "utilities"]:
            match = re.search(fr"{name}\s*\$?(\d+(?:,\d{3})*(?:\.\d+)?)", user_input, re.IGNORECASE)
            if match:
                overrides[name.capitalize()] = float(match.group(1).replace(",", ""))
        if overrides:
            context["override_fixed_expenses"] = overrides


        # Determine if multiple agents might be needed
        if len([qt for qt in self.query_patterns.keys()
                if any(re.search(p, user_input, re.IGNORECASE)
                      for p in self.query_patterns[qt])]) > 1:
            context["requires_multiple_agents"] = True

        # Check if user confirmed executing an investment action
        confirm_keywords = ["invest now", "execute", "confirm", "do it", "deposit"]
        if any(kw in user_input for kw in confirm_keywords):
            context["execute_plaid"] = True

        return context
    
    def _needs_explanation(self, user_input: str) -> bool:
        """Determines if the response needs to be explained in simple terms"""
        explanation_keywords = [
            "explain", "eli5", "simple", "understand", "clarify", 
            "break down", "help me", "what does"
        ]
        
        return any(keyword in user_input.lower() for keyword in explanation_keywords)
    
    def _extract_simulation_params(self, user_input: str) -> Dict[str, Any]:
        """Extracts parameters for simulation scenarios"""
        params = {}
        
        # Extract scenario type
        if "job loss" in user_input or "quit" in user_input:
            params["scenario_type"] = "job_loss"
        elif "emergency" in user_input:
            params["scenario_type"] = "emergency"
        elif "market crash" in user_input:
            params["scenario_type"] = "market_downturn"
        
        return params

# state = {
#     "input": "I got a $5,000 bonus and want to optimize my budget for the next 6 months. Can you explain it in simple terms?"
# }
# O/P:
# {
#   "query_type": "budget_optimization",
#   "context": {
#     "requires_multiple_agents": false,
#     "amount": "5000",
#     "timeframe": ["6", "month"]
#   },
#   "requires_explanation": true,
#   "simulation_params": null
# }