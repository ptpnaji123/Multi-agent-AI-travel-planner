from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState
from app.agents.intake_agent import intake_agent
from app.agents.destination_agent import destination_agent


def intake_node(state: TravelState) -> TravelState:

    print("\n--- INTAKE AGENT ---")

    trip_request = intake_agent(
        state["user_request"]
    )

    print("\nStructured Trip Request:")
    print(trip_request)

    return {
        **state,
        "trip_request": trip_request
    }


def coordinator_node(state: TravelState) -> TravelState:

    print("\n--- COORDINATOR NODE ---")

    print("Coordinator received:")
    print(state["trip_request"])

    return state


def destination_node(state: TravelState) -> TravelState:

    print("\n--- DESTINATION RESEARCH AGENT ---")

    destination = state["trip_request"].destination

    research = destination_agent(destination)

    print("\nDestination Research:")
    print(research)

    return {
        **state,
        "destination_research": research
    }


def build_graph():

    builder = StateGraph(TravelState)

    builder.add_node("intake", intake_node)
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("destination", destination_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "coordinator")
    builder.add_edge("coordinator", "destination")
    builder.add_edge("destination", END)

    return builder.compile()