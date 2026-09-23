from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState

from app.agents.intake_agent import intake_agent

from app.agents.destination_agent import (
    destination_agent,
)

from app.agents.flight_agent import (
    flight_agent,
)

from app.agents.hotel_agent import (
    hotel_agent,
)

from app.agents.budget_agent import (
    budget_agent,
)

from app.agents.selection_agent import (
    select_flight,
    select_hotel,
)


# =========================================================
# INTAKE NODE
# =========================================================

def intake_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- INTAKE AGENT ---"
    )

    user_request = state[
        "user_request"
    ]

    trip_request = intake_agent(
        user_request
    )

    print(
        "\nStructured Trip Request:"
    )

    print(
        trip_request
    )

    return {
        **state,
        "trip_request": trip_request,
    }


# =========================================================
# COORDINATOR NODE
# =========================================================

def coordinator_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- COORDINATOR NODE ---"
    )

    trip_request = state[
        "trip_request"
    ]

    print(
        "Coordinator received:"
    )

    print(
        trip_request
    )

    return state


# =========================================================
# DESTINATION RESEARCH NODE
# =========================================================

def destination_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- DESTINATION RESEARCH AGENT ---"
    )

    destination = state[
        "trip_request"
    ].destination

    research = destination_agent(
        destination
    )

    print(
        "\nDestination Research:"
    )

    print(
        research
    )

    return {
        **state,
        "destination_research": research,
    }


# =========================================================
# FLIGHT NODE
# =========================================================

def flight_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- FLIGHT AGENT ---"
    )

    trip_request = state[
        "trip_request"
    ]

    flights = flight_agent(
        trip_request
    )

    print(
        "\nTop Flight Options:"
    )

    if not flights:

        print(
            "No round-trip flights found."
        )

    for index, flight in enumerate(
        flights,
        start=1,
    ):

        print(
            "\n=============================="
        )

        print(
            f"OPTION {index}"
        )

        # -----------------------------------------
        # Outbound
        # -----------------------------------------

        print(
            "\nOutbound:"
        )

        print(
            f"  Airline: "
            f"{flight.outbound.airline}"
        )

        print(
            f"  Flight: "
            f"{flight.outbound.flight_number}"
        )

        print(
            f"  Route: "
            f"{flight.outbound.origin}"
            f" -> "
            f"{flight.outbound.destination}"
        )

        print(
            f"  Departure: "
            f"{flight.outbound.departure_time}"
        )

        print(
            f"  Arrival: "
            f"{flight.outbound.arrival_time}"
        )

        print(
            f"  Duration: "
            f"{flight.outbound.duration}"
        )

        # -----------------------------------------
        # Return
        # -----------------------------------------

        print(
            "\nReturn:"
        )

        print(
            f"  Airline: "
            f"{flight.return_flight.airline}"
        )

        print(
            f"  Flight: "
            f"{flight.return_flight.flight_number}"
        )

        print(
            f"  Route: "
            f"{flight.return_flight.origin}"
            f" -> "
            f"{flight.return_flight.destination}"
        )

        print(
            f"  Departure: "
            f"{flight.return_flight.departure_time}"
        )

        print(
            f"  Arrival: "
            f"{flight.return_flight.arrival_time}"
        )

        print(
            f"  Duration: "
            f"{flight.return_flight.duration}"
        )

        # -----------------------------------------
        # Price
        # -----------------------------------------

        print(
            "\nPrice:"
        )

        print(
            f"  Original Price: "
            f"{flight.total_price:.2f} "
            f"{flight.currency}"
        )

        print(
            f"  INR Price: "
            f"₹{flight.total_price_inr:,.2f}"
        )

        print(
            f"  Provider: "
            f"{flight.provider}"
        )

    return {
        **state,
        "flights": flights,
    }


# =========================================================
# FLIGHT SELECTION NODE
# =========================================================

def flight_selection_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- FLIGHT SELECTION ---"
    )

    flights = state[
        "flights"
    ]

    selected_flight = select_flight(
        flights
    )

    print(
        "\nSelected Flight:"
    )

    print(
        f"Airline: "
        f"{selected_flight.outbound.airline}"
    )

    print(
        f"Flight: "
        f"{selected_flight.outbound.flight_number}"
    )

    print(
        f"Route: "
        f"{selected_flight.outbound.origin}"
        f" -> "
        f"{selected_flight.outbound.destination}"
    )

    print(
        f"INR Price: "
        f"₹{selected_flight.total_price_inr:,.2f}"
    )

    return {
        **state,
        "selected_flight": selected_flight,
    }


# =========================================================
# HOTEL NODE
# =========================================================

def hotel_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- HOTEL AGENT ---"
    )

    trip_request = state[
        "trip_request"
    ]

    hotels = hotel_agent(
        trip_request
    )

    print(
        "\nTop Hotel Options:"
    )

    if not hotels:

        print(
            "No hotels found."
        )

    for index, hotel in enumerate(
        hotels,
        start=1,
    ):

        print(
            "\n=============================="
        )

        print(
            f"OPTION {index}"
        )

        print(
            f"Hotel: "
            f"{hotel.name}"
        )

        print(
            f"Hotel Code: "
            f"{hotel.hotel_code}"
        )

        print(
            f"Category: "
            f"{hotel.category}"
        )

        print(
            f"Room: "
            f"{hotel.room_name}"
        )

        print(
            f"Board: "
            f"{hotel.board}"
        )

        # -----------------------------------------
        # Price
        # -----------------------------------------

        print(
            f"Original Price: "
            f"{hotel.total_price:.2f} "
            f"{hotel.currency}"
        )

        print(
            f"INR Price: "
            f"₹{hotel.total_price_inr:,.2f}"
        )

        print(
            f"Rate Type: "
            f"{hotel.rate_type}"
        )

        print(
            f"Rate Class: "
            f"{hotel.rate_class}"
        )

        print(
            f"Free Cancellation: "
            f"{hotel.free_cancellation}"
        )

        print(
            f"Provider: "
            f"{hotel.provider}"
        )

    return {
        **state,
        "hotels": hotels,
    }


# =========================================================
# HOTEL SELECTION NODE
# =========================================================

def hotel_selection_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- HOTEL SELECTION ---"
    )

    hotels = state[
        "hotels"
    ]

    selected_hotel = select_hotel(
        hotels
    )

    print(
        "\nSelected Hotel:"
    )

    print(
        f"Hotel: "
        f"{selected_hotel.name}"
    )

    print(
        f"Room: "
        f"{selected_hotel.room_name}"
    )

    print(
        f"Board: "
        f"{selected_hotel.board}"
    )

    print(
        f"INR Price: "
        f"₹{selected_hotel.total_price_inr:,.2f}"
    )

    return {
        **state,
        "selected_hotel": selected_hotel,
    }


# =========================================================
# BUDGET NODE
# =========================================================

def budget_node(
    state: TravelState,
) -> TravelState:

    print(
        "\n--- BUDGET AGENT ---"
    )

    trip_request = state[
        "trip_request"
    ]

    flights = state[
        "flights"
    ]

    hotels = state[
        "hotels"
    ]

    budget = budget_agent(

        trip_request=trip_request,

        flights=flights,

        hotels=hotels,
    )

    print(
        "\n=============================="
    )

    print(
        "TRIP BUDGET"
    )

    print(
        "=============================="
    )

    print(
        f"Flight Cost: "
        f"₹{budget.flight_cost:,.2f}"
    )

    print(
        f"Hotel Cost: "
        f"₹{budget.hotel_cost:,.2f}"
    )

    print(
        f"Food Cost: "
        f"₹{budget.food_cost:,.2f}"
    )

    print(
        f"Transport Cost: "
        f"₹{budget.transport_cost:,.2f}"
    )

    print(
        f"Activity Cost: "
        f"₹{budget.activity_cost:,.2f}"
    )

    print(
        "------------------------------"
    )

    print(
        f"TOTAL ESTIMATED COST: "
        f"₹{budget.total_cost:,.2f}"
    )

    print(
        f"\nNotes: "
        f"{budget.notes}"
    )

    return {
        **state,
        "budget_report": budget,
    }


# =========================================================
# BUILD LANGGRAPH
# =========================================================

def build_graph():

    builder = StateGraph(
        TravelState
    )

    # -----------------------------------------
    # Register nodes
    # -----------------------------------------

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

    # -----------------------------------------
    # Workflow edges
    # -----------------------------------------

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
        END,
    )

    # -----------------------------------------
    # Compile graph
    # -----------------------------------------

    return builder.compile()