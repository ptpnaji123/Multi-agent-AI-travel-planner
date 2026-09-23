from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState

from app.agents.intake_agent import intake_agent
from app.agents.destination_agent import destination_agent
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.budget_agent import budget_agent
from app.agents.itinerary_agent import itinerary_agent
from app.agents.critic_agent import critic_agent

from app.agents.selection_agent import (
    select_flight,
    select_hotel,
)

from app.validators.schedule_validator import (
    validate_schedule,
)

from app.services.itinerary_repair_service import (
    deterministic_repair_itinerary,
)


# ============================================================
# INTAKE
# ============================================================

def intake_node(state: TravelState):

    print("\n--- INTAKE ---")

    trip_request = intake_agent(
        state["user_request"]
    )

    print("\nTrip Request:")
    print(f"Origin: {trip_request.origin}")
    print(f"Destination: {trip_request.destination}")
    print(f"Start Date: {trip_request.start_date}")
    print(f"End Date: {trip_request.end_date}")
    print(f"Travelers: {trip_request.travelers}")
    print(f"Currency: {trip_request.currency}")

    return {
        **state,
        "trip_request": trip_request,
    }


# ============================================================
# COORDINATOR
# ============================================================

def coordinator_node(state: TravelState):

    print("\n--- COORDINATOR ---")
    print("Trip request validated.")

    return {
        **state,
        "repair_attempt": 0,
    }


# ============================================================
# DESTINATION RESEARCH
# ============================================================

def destination_node(state: TravelState):

    print("\n--- DESTINATION RESEARCH ---")

    research = destination_agent(
        state["trip_request"]
    )

    return {
        **state,
        "destination_research": research,
    }


# ============================================================
# FLIGHT SEARCH
# ============================================================

def flight_node(state: TravelState):

    print("\n--- FLIGHT SEARCH ---")

    flights = flight_agent(
        state["trip_request"]
    )

    return {
        **state,
        "flights": flights,
    }


# ============================================================
# FLIGHT SELECTION
# ============================================================

def flight_selection_node(state: TravelState):

    print("\n--- FLIGHT SELECTION ---")

    selected_flight = select_flight(
        state["flights"]
    )

    return {
        **state,
        "selected_flight": selected_flight,
    }


# ============================================================
# HOTEL SEARCH
# ============================================================

def hotel_node(state: TravelState):

    print("\n--- HOTEL SEARCH ---")

    hotels = hotel_agent(
        state["trip_request"]
    )

    return {
        **state,
        "hotels": hotels,
    }


# ============================================================
# HOTEL SELECTION
# ============================================================

def hotel_selection_node(state: TravelState):

    print("\n--- HOTEL SELECTION ---")

    selected_hotel = select_hotel(
        state["hotels"]
    )

    return {
        **state,
        "selected_hotel": selected_hotel,
    }


# ============================================================
# BUDGET
# ============================================================

def budget_node(state: TravelState):

    print("\n--- BUDGET ---")

    budget_report = budget_agent(
        trip_request=state["trip_request"],
        selected_flight=state["selected_flight"],
        selected_hotel=state["selected_hotel"],
    )

    print(
        f"Flight Cost: ₹{budget_report.flight_cost:.2f}"
    )

    print(
        f"Hotel Cost: ₹{budget_report.hotel_cost:.2f}"
    )

    print(
        f"Food Cost: ₹{budget_report.food_cost:.2f}"
    )

    print(
        f"Transport Cost: ₹{budget_report.transport_cost:.2f}"
    )

    print(
        f"Activity Cost: ₹{budget_report.activity_cost:.2f}"
    )

    print(
        f"TOTAL ESTIMATED COST: "
        f"₹{budget_report.total_cost:.2f}"
    )

    return {
        **state,
        "budget_report": budget_report,
    }


# ============================================================
# ITINERARY GENERATION
# ============================================================

def itinerary_node(state: TravelState):

    print("\n--- ITINERARY ---")

    itinerary = itinerary_agent(
        trip_request=state["trip_request"],
        destination_research=state["destination_research"],
        selected_flight=state["selected_flight"],
        selected_hotel=state["selected_hotel"],
        budget_report=state["budget_report"],
    )

    print("\n--- ITINERARY GENERATED ---")

    print(
        f"Destination: {itinerary.destination}"
    )

    print(
        f"Days generated: {len(itinerary.days)}"
    )

    for day in itinerary.days:

        print(
            f"\nDay {day.day} ({day.date})"
        )

        print(
            f"Area: {day.area}"
        )

        for activity in day.activities:

            print(
                f"  {activity.start_time} - "
                f"{activity.end_time}: "
                f"{activity.name}"
            )

            print(
                f"  Location: {activity.location}"
            )

            print(
                f"  Cost: ₹{activity.estimated_cost:.2f}"
            )

            print(
                f"  Currency: {activity.currency}"
            )

    return {
        **state,
        "itinerary": itinerary,
    }


# ============================================================
# SCHEDULE VALIDATION
# ============================================================

def schedule_validation_node(state: TravelState):

    print("\n--- SCHEDULE VALIDATION ---")

    # IMPORTANT:
    #
    # validate_schedule() currently accepts only:
    #
    #   itinerary
    #   selected_flight
    #   selected_hotel
    #
    # It does NOT accept trip_request.

    validation = validate_schedule(
        itinerary=state["itinerary"],
        selected_flight=state["selected_flight"],
        selected_hotel=state["selected_hotel"],
    )

    print("\nSchedule Validation Result:")

    print(
        f"Valid: {validation.get('valid', False)}"
    )

    errors = validation.get(
        "errors",
        [],
    )

    warnings = validation.get(
        "warnings",
        [],
    )

    if errors:

        print("\nErrors:")

        for error in errors:
            print(f"- {error}")

    if warnings:

        print("\nWarnings:")

        for warning in warnings:
            print(f"- {warning}")

    return {
        **state,
        "schedule_validation": validation,
    }


# ============================================================
# CRITIC
# ============================================================

def critic_node(state: TravelState):

    print("\n--- CRITIC ---")

    repair_attempt = state.get(
        "repair_attempt",
        0,
    )

    critique = critic_agent(
        trip_request=state["trip_request"],
        itinerary=state["itinerary"],
        destination_research=state["destination_research"],
        schedule_validation=state["schedule_validation"],
        repair_attempt=repair_attempt,
    )

    print("\nCritic Result:")

    print(
        f"Valid: {critique.get('valid', False)}"
    )

    print(
        f"Needs Repair: "
        f"{critique.get('needs_repair', False)}"
    )

    errors = critique.get(
        "errors",
        [],
    )

    warnings = critique.get(
        "warnings",
        [],
    )

    if errors:

        print("\nCritic Errors:")

        for error in errors:
            print(f"- {error}")

    if warnings:

        print("\nCritic Warnings:")

        for warning in warnings:
            print(f"- {warning}")

    return {
        **state,
        "critique": critique,
    }


# ============================================================
# DETERMINISTIC ITINERARY REPAIR
# ============================================================

def repair_itinerary_node(state: TravelState):

    current_attempt = state.get(
        "repair_attempt",
        0,
    )

    new_attempt = current_attempt + 1

    print("\n--- ITINERARY REPAIR ---")

    print(
        f"Repair attempt: {new_attempt}"
    )

    print(
        "Applying deterministic schedule repair..."
    )

    repaired_itinerary = (
        deterministic_repair_itinerary(
            itinerary=state["itinerary"],
            trip_request=state["trip_request"],
            selected_flight=state["selected_flight"],
            selected_hotel=state["selected_hotel"],
        )
    )

    print(
        "Deterministic itinerary repair completed."
    )

    return {
        **state,
        "itinerary": repaired_itinerary,
        "repair_attempt": new_attempt,
    }


# ============================================================
# CRITIC ROUTER
# ============================================================

def critic_router(state: TravelState):

    critique = state.get(
        "critique",
        {},
    )

    valid = critique.get(
        "valid",
        False,
    )

    repair_attempt = state.get(
        "repair_attempt",
        0,
    )

    # --------------------------------------------------------
    # VALID
    # --------------------------------------------------------

    if valid:

        print(
            "\nCritic: itinerary is valid."
        )

        print(
            "No repair required."
        )

        return "end"

    # --------------------------------------------------------
    # ONE REPAIR ALLOWED
    # --------------------------------------------------------

    if repair_attempt < 1:

        print(
            "\nCritic: itinerary requires repair."
        )

        print(
            "Routing to deterministic repair."
        )

        return "repair"

    # --------------------------------------------------------
    # STOP AFTER ONE REPAIR
    # --------------------------------------------------------

    print(
        "\nCritic: itinerary still has validation "
        "issues after deterministic repair."
    )

    print(
        "Maximum repair attempts reached."
    )

    print(
        "Stopping repair loop."
    )

    return "end"


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    builder = StateGraph(
        TravelState
    )

    # ========================================================
    # NODES
    # ========================================================

    builder.add_node(
        "intake",
        intake_node,
    )

    builder.add_node(
        "coordinator",
        coordinator_node,
    )

    builder.add_node(
        "destination",
        destination_node,
    )

    builder.add_node(
        "flight",
        flight_node,
    )

    builder.add_node(
        "flight_selection",
        flight_selection_node,
    )

    builder.add_node(
        "hotel",
        hotel_node,
    )

    builder.add_node(
        "hotel_selection",
        hotel_selection_node,
    )

    builder.add_node(
        "budget",
        budget_node,
    )

    builder.add_node(
        "itinerary",
        itinerary_node,
    )

    builder.add_node(
        "schedule_validation",
        schedule_validation_node,
    )

    builder.add_node(
        "critic",
        critic_node,
    )

    builder.add_node(
        "repair_itinerary",
        repair_itinerary_node,
    )

    # ========================================================
    # MAIN FLOW
    # ========================================================

    builder.add_edge(
        START,
        "intake",
    )

    builder.add_edge(
        "intake",
        "coordinator",
    )

    builder.add_edge(
        "coordinator",
        "destination",
    )

    builder.add_edge(
        "destination",
        "flight",
    )

    builder.add_edge(
        "flight",
        "flight_selection",
    )

    builder.add_edge(
        "flight_selection",
        "hotel",
    )

    builder.add_edge(
        "hotel",
        "hotel_selection",
    )

    builder.add_edge(
        "hotel_selection",
        "budget",
    )

    builder.add_edge(
        "budget",
        "itinerary",
    )

    builder.add_edge(
        "itinerary",
        "schedule_validation",
    )

    builder.add_edge(
        "schedule_validation",
        "critic",
    )

    # ========================================================
    # CRITIC ROUTING
    # ========================================================

    builder.add_conditional_edges(
        "critic",
        critic_router,
        {
            "repair": "repair_itinerary",
            "end": END,
        },
    )

    # ========================================================
    # REPAIR → VALIDATION
    # ========================================================

    builder.add_edge(
        "repair_itinerary",
        "schedule_validation",
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return builder.compile()


# ============================================================
# DEFAULT GRAPH INSTANCE
# ============================================================

graph = build_graph()