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
            f" → "
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
            f" → "
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
            f"  Total Price: "
            f"{flight.total_price} "
            f"{flight.currency}"
        )

        print(
            f"  Provider: "
            f"{flight.provider}"
        )

    return {
        **state,
        "flights": flights,
    }


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
            f"Hotel: {hotel.name}"
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

        print(
            f"Total Price: "
            f"{hotel.total_price} "
            f"{hotel.currency}"
        )

        print(
            f"Rate Type: "
            f"{hotel.rate_type}"
        )

        print(
            f"Provider: "
            f"{hotel.provider}"
        )

    return {
        **state,
        "hotels": hotels,
    }


def build_graph():

    builder = StateGraph(
        TravelState
    )

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
        "hotel",
        hotel_node,
    )

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
        "hotel",
    )

    builder.add_edge(
        "hotel",
        END,
    )

    return builder.compile()