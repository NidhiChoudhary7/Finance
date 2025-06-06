# graph.py
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional, Any
from agents.planner import PlannerAgent
from agents.LifeEventAgent import LifeEventAgent
from agents.budget_optimizer_agent import BudgetOptimizerAgent
from agents.investment_agent import InvestmentAgent
from agents.explainer_agent import ExplainerAgent
from agents.simulation_agent import SimulationAgent

class AgentState(TypedDict):
    input: str
    query_type: Optional[str]
    context: Optional[dict]
    intermediate_results: List[dict]
    final_result: str
    confidence_score: Optional[float]
    requires_explanation: bool
    simulation_params: Optional[dict]

class FinLifeNavigator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.life_event_agent = LifeEventAgent()
        self.budget_optimizer = BudgetOptimizerAgent()
        self.investment_agent = InvestmentAgent()
        self.explainer_agent = ExplainerAgent()
        self.simulation_agent = SimulationAgent()
        
        self.workflow = self._build_graph()
        self.graph = self.workflow.compile()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add planner node (master coordinator)
        workflow.add_node("planner", self._planner_node)
        
        # Add specialized agent nodes
        workflow.add_node("life_event_agent", self._life_event_node)
        workflow.add_node("budget_optimizer_agent", self._budget_optimizer_node)
        workflow.add_node("investment_agent", self._investment_node)
        workflow.add_node("simulation_agent", self._simulation_node)
        workflow.add_node("explainer_agent", self._explainer_node)
        
        # Add coordinator node for multi-agent scenarios
        workflow.add_node("coordinator", self._coordinator_node)
        
        # Define the flow
        workflow.add_edge(START, "planner")
        
        # Conditional edges from planner
        workflow.add_conditional_edges(
            "planner",
            self._route_from_planner,
            {
                "life_event_agent": "life_event_agent",
                "budget_optimizer_agent": "budget_optimizer_agent",
                "investment_agent": "investment_agent",
                "simulation_agent": "simulation_agent",
                "coordinator": "coordinator"
            }
        )
        
        # Routes to coordinator for complex queries
        workflow.add_edge("life_event_agent", "coordinator")
        workflow.add_edge("budget_optimizer_agent", "coordinator")
        workflow.add_edge("investment_agent", "coordinator")
        workflow.add_edge("simulation_agent", "coordinator")
        
        # Conditional routing from coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self._route_from_coordinator,
            {
                "explainer_agent": "explainer_agent",
                "END": END
            }
        )
        
        workflow.add_edge("explainer_agent", END)
        
        return workflow
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Master planner that analyzes and routes queries"""
        result = self.planner.process(state)
        return {
            **state,
            "query_type": result.get("query_type"),
            "context": result.get("context", {}),
            "requires_explanation": result.get("requires_explanation", False),
            "simulation_params": result.get("simulation_params")
        }
    
    def _life_event_node(self, state: AgentState) -> AgentState:
        """Processes life events and calendar data"""
        result = self.life_event_agent.process(state)
        return {
            **state,
            "intermediate_results": state.get("intermediate_results", []) + [result],
            "confidence_score": result.get("confidence_score")
        }
    
    def _budget_optimizer_node(self, state: AgentState) -> AgentState:
        """Optimizes budget and investment allocations"""
        result = self.budget_optimizer.process(state)
        return {
            **state,
            "intermediate_results": state.get("intermediate_results", []) + [result],
            "confidence_score": result.get("confidence_score")
        }
    
    def _investment_node(self, state: AgentState) -> AgentState:
        """Handles investment analysis and portfolio management"""
        result = self.investment_agent.process(state)
        return {
            **state,
            "intermediate_results": state.get("intermediate_results", []) + [result],
            "confidence_score": result.get("confidence_score")
        }
    
    def _simulation_node(self, state: AgentState) -> AgentState:
        """Runs financial scenario simulations"""
        result = self.simulation_agent.process(state)
        return {
            **state,
            "intermediate_results": state.get("intermediate_results", []) + [result],
            "confidence_score": result.get("confidence_score")
        }
    
    def _coordinator_node(self, state: AgentState) -> AgentState:
        """Coordinates results from multiple agents"""
        intermediate_results = state.get("intermediate_results", [])

        # Example of running an additional agent when multiple agents are needed
        if state.get("context", {}).get("requires_multiple_agents") and state.get(
            "query_type"
        ) == "life_event" and len(intermediate_results) == 1:
            # Invoke budget optimizer as a secondary step
            result = self.budget_optimizer.process(state)
            intermediate_results.append(result)

        if len(intermediate_results) == 1:
            final_result = intermediate_results[0].get("result", "")
        else:
            final_result = self._combine_results(intermediate_results)

        return {
            **state,
            "intermediate_results": intermediate_results,
            "final_result": final_result,
        }
    
    def _explainer_node(self, state: AgentState) -> AgentState:
        """Converts technical outputs to user-friendly explanations"""
        result = self.explainer_agent.process(state)
        return {
            **state,
            "final_result": result.get("explanation", state.get("final_result", ""))
        }
    
    def _route_from_planner(self, state: AgentState) -> str:
        """Routes from planner to appropriate agent(s)"""
        query_type = state.get("query_type", "general")
        context = state.get("context", {})
        
        # Check if multiple agents are needed. In this toy example we simply
        # start with one agent and let the coordinator trigger others.
        if context.get("requires_multiple_agents"):
            if query_type == "life_event":
                return "life_event_agent"
            if query_type == "budget_optimization":
                return "budget_optimizer_agent"
            return "coordinator"
        
        # Route to specific agent
        routing_map = {
            "life_event": "life_event_agent",
            "budget_optimization": "budget_optimizer_agent",
            "investment_analysis": "investment_agent",
            "simulation": "simulation_agent"
        }
        
        return routing_map.get(query_type, "coordinator")
    
    def _route_from_coordinator(self, state: AgentState) -> str:
        """Routes from coordinator to explainer or end"""
        if state.get("requires_explanation", False):
            return "explainer_agent"
        return "END"
    
    def _combine_results(self, results: List[dict]) -> str:
        """Intelligently combines results from multiple agents"""
        combined = []
        for result in results:
            if result.get("result"):
                combined.append(result["result"])
        
        return " | ".join(combined) if combined else "No results available"

# Create global instance
navigator = FinLifeNavigator()
graph = navigator.graph
