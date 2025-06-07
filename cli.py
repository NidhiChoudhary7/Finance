from graph import graph


def gather_profile():
    print("Welcome to FinLife Navigator CLI")
    name = input("Name (optional): ").strip()
    risk = input("Risk tolerance (low/medium/high) [medium]: ").strip().lower() or "medium"
    goal = input("Primary financial goal (optional): ").strip()
    horizon = input("Time horizon in years (optional): ").strip()
    timeframe = None
    if horizon:
        try:
            timeframe = (int(horizon), "year")
        except ValueError:
            pass
    return {
        "name": name,
        "risk_tolerance": risk,
        "goal": goal or None,
        "timeframe": timeframe,
    }


def run_cli():
    profile = gather_profile()
    print("\nType 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        initial_state = {
            "input": user_input,
            "query_type": None,
            "context": profile,
            "intermediate_results": [],
            "final_result": "",
            "confidence_score": None,
            "requires_explanation": False,
            "simulation_params": None,
        }
        final_state = graph.invoke(initial_state)
        output = final_state.get("final_result", "")
        print(f"Assistant: {output}")
        # Debug: show state if no result
        if not output or output == "No results available":
            print("Debug final state:", final_state)
        if final_state.get("confidence_score") is not None:
            print(f"(Confidence: {final_state['confidence_score']:.2f})")
        print()


if __name__ == "__main__":
    run_cli()
