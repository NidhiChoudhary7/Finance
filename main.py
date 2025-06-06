# main.py
from graph import graph
import json

def run_finlife_navigator():
    print("🚀 FinLife Navigator - Hierarchical Agent System\n")
    print("=" * 50)

    test_scenarios = [
        # {
        #     "input": "I'm planning a vacation next month and received a $5000 bonus. How should I allocate this?",
        #     "description": "Multi-agent scenario (Life Event + Budget Optimization)"
        # },
        # {
        #     "input": "Explain how my portfolio performed this quarter in simple terms",
        #     "description": "Investment analysis with explanation required"
        # },
        # {
        #     "input": "What if I quit my job for 6 months to start a business?",
        #     "description": "Simulation scenario"
        # },
        {
            "input": "I got married and want to optimize our combined finances",
            "description": "Life event with budget optimization"
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧠 Scenario {i}: {scenario['description']}")
        print(f"📝 Input: {scenario['input']}")
        print("-" * 40)
        
        try:
            # Initialize state
            initial_state = {
                "input": scenario["input"],
                "query_type": None,
                "context": None,
                "intermediate_results": [],
                "final_result": "",
                "confidence_score": None,
                "requires_explanation": False,
                "simulation_params": None
            }
            
            # Run the graph
            final_state = graph.invoke(initial_state)
            
            # Display results
            print(f"🎯 Query Type: {final_state.get('query_type', 'Unknown')}")
            print(f"📊 Context: {json.dumps(final_state.get('context', {}), indent=2)}")
            print(f"✅ Final Result: {final_state.get('final_result', 'No result')}")
            
            if final_state.get('confidence_score'):
                print(f"📈 Confidence: {final_state['confidence_score']:.2f}")
                
        except Exception as e:
            print(f"❌ Error processing scenario: {str(e)}")
        
        print("=" * 50)

if __name__ == "__main__":
    run_finlife_navigator()
