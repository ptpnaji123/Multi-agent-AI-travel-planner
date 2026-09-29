import sys
from pathlib import Path
from datetime import date

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st

from app.graph.graph import build_graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SMALL HELPERS
# ============================================================

def format_inr(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def format_date(value):
    if not value:
        return ""

    try:
        if isinstance(value, date):
            return value.strftime("%d %b %Y")

        return date.fromisoformat(
            str(value)
        ).strftime("%d %b %Y")

    except Exception:
        return str(value)


def get_value(obj, name, default=""):
    if obj is None:
        return default

    return getattr(obj, name, default)


# ============================================================
# HEADER
# ============================================================

st.title("✈️ AI Travel Planner")

st.caption(
    "Plan your trip with live flights, hotels, budget estimates "
    "and a day-by-day itinerary."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🧳 Plan Your Trip")

    origin = st.text_input(
        "From",
        value="Kochi",
        placeholder="e.g. Kochi",
    )

    destination = st.text_input(
        "Destination",
        value="Dubai",
        placeholder="e.g. Dubai",
    )

    start_date = st.date_input(
        "Start date",
        value=date(2026, 12, 10),
    )

    end_date = st.date_input(
        "End date",
        value=date(2026, 12, 15),
    )

    travelers = st.number_input(
        "Travelers",
        min_value=1,
        max_value=20,
        value=1,
        step=1,
    )

    pace = st.selectbox(
        "Travel pace",
        [
            "relaxed",
            "moderate",
            "fast",
        ],
        index=1,
    )

    interests = st.multiselect(
        "Interests",
        [
            "beaches",
            "food",
            "shopping",
            "history",
            "culture",
            "adventure",
            "nature",
            "nightlife",
            "architecture",
            "family",
        ],
    )

    st.divider()

    generate = st.button(
        "🚀 Generate Travel Plan",
        type="primary",
        use_container_width=True,
    )

    st.caption("All displayed costs are in INR.")


# ============================================================
# GENERATE TRIP
# ============================================================

if generate:

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not origin.strip():
        st.error("Please enter your starting location.")
        st.stop()

    if not destination.strip():
        st.error("Please enter a destination.")
        st.stop()

    if end_date < start_date:
        st.error("End date cannot be before start date.")
        st.stop()

    interest_text = ""

    if interests:
        interest_text = (
            " I am interested in "
            + ", ".join(interests)
            + "."
        )

    user_request = (
        f"I want to travel from {origin.strip()} "
        f"to {destination.strip()} "
        f"from {start_date.isoformat()} "
        f"to {end_date.isoformat()}. "
        f"There are {travelers} traveler(s). "
        f"My preferred travel pace is {pace}."
        f"{interest_text}"
    )

    # --------------------------------------------------------
    # RUN PLANNER
    # --------------------------------------------------------

    with st.spinner(
        "Planning your trip... This may take a few minutes."
    ):

        try:

            graph = build_graph()

            state = graph.invoke(
                {
                    "user_request": user_request
                }
            )

            st.session_state["travel_state"] = state
            st.session_state["travel_request"] = user_request

        except Exception as exc:

            st.error(
                "Something went wrong while creating your trip."
            )

            with st.expander("Error details"):
                st.exception(exc)

            st.stop()


# ============================================================
# GET STORED RESULT
# ============================================================

state = st.session_state.get(
    "travel_state"
)


# ============================================================
# EMPTY STATE
# ============================================================

if not state:

    st.info(
        "Enter your trip details in the sidebar and click "
        "**Generate Travel Plan**."
    )

    st.markdown(
        """
        ### What you'll get

        - ✈️ Flight options
        - 🏨 Hotel recommendation
        - 💰 Estimated trip budget
        - 📅 Day-by-day itinerary
        - 🌍 Destination highlights
        """
    )

    st.stop()


# ============================================================
# EXTRACT STATE
# ============================================================

trip_request = state.get(
    "trip_request"
)

destination_research = state.get(
    "destination_research"
)

selected_flight = state.get(
    "selected_flight"
)

selected_hotel = state.get(
    "selected_hotel"
)

budget = state.get("budget")

if budget is None:
    budget = state.get("budget_report")

itinerary = state.get(
    "itinerary"
)

schedule_validation = state.get(
    "schedule_validation"
)


# ============================================================
# TRIP OVERVIEW
# ============================================================

st.header("🗺️ Your Trip")

overview_col1, overview_col2, overview_col3, overview_col4 = (
    st.columns(4)
)


# FROM / TO

with overview_col1:

    origin_value = get_value(
        trip_request,
        "origin",
        origin,
    )

    destination_value = get_value(
        trip_request,
        "destination",
        destination,
    )

    st.metric(
        "Route",
        f"{origin_value} → {destination_value}",
    )


# DATES

with overview_col2:

    start_value = get_value(
        trip_request,
        "start_date",
        start_date,
    )

    end_value = get_value(
        trip_request,
        "end_date",
        end_date,
    )

    st.metric(
        "Travel dates",
        f"{format_date(start_value)} – "
        f"{format_date(end_value)}",
    )


# TRAVELERS

with overview_col3:

    travelers_value = get_value(
        trip_request,
        "travelers",
        travelers,
    )

    st.metric(
        "Travelers",
        str(travelers_value),
    )


# PACE

with overview_col4:

    pace_value = get_value(
        trip_request,
        "pace",
        pace,
    )

    st.metric(
        "Travel pace",
        str(pace_value).capitalize(),
    )


st.divider()


# ============================================================
# FLIGHT
# ============================================================

st.header("✈️ Flights")

if selected_flight:

    outbound = get_value(
        selected_flight,
        "outbound",
        None,
    )

    return_flight = get_value(
        selected_flight,
        "return_flight",
        None,
    )

    flight_price = get_value(
        selected_flight,
        "total_price_inr",
        0,
    )

    provider = get_value(
        selected_flight,
        "provider",
        "Flight provider",
    )

    if outbound and return_flight:

        flight_col1, flight_col2 = st.columns(2)

        # ----------------------------------------------------
        # OUTBOUND
        # ----------------------------------------------------

        with flight_col1:

            st.subheader("Outbound")

            st.write(
                f"**{get_value(outbound, 'origin')} "
                f"→ "
                f"{get_value(outbound, 'destination')}**"
            )

            st.write(
                f"Departure: "
                f"{get_value(outbound, 'departure_time')}"
            )

            st.write(
                f"Arrival: "
                f"{get_value(outbound, 'arrival_time')}"
            )

            airline = get_value(
                outbound,
                "airline",
                "",
            )

            flight_number = get_value(
                outbound,
                "flight_number",
                "",
            )

            if airline or flight_number:

                st.caption(
                    f"{airline} {flight_number}"
                )

        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        with flight_col2:

            st.subheader("Return")

            st.write(
                f"**{get_value(return_flight, 'origin')} "
                f"→ "
                f"{get_value(return_flight, 'destination')}**"
            )

            st.write(
                f"Departure: "
                f"{get_value(return_flight, 'departure_time')}"
            )

            st.write(
                f"Arrival: "
                f"{get_value(return_flight, 'arrival_time')}"
            )

            airline = get_value(
                return_flight,
                "airline",
                "",
            )

            flight_number = get_value(
                return_flight,
                "flight_number",
                "",
            )

            if airline or flight_number:

                st.caption(
                    f"{airline} {flight_number}"
                )

        st.success(
            f"Selected flight • {format_inr(flight_price)}"
        )

        if provider:
            st.caption(
                f"Provider: {provider}"
            )

else:

    st.warning(
        "No flight was selected."
    )


st.divider()


# ============================================================
# HOTEL
# ============================================================

st.header("🏨 Hotel")

if selected_hotel:

    hotel_col1, hotel_col2 = st.columns(
        [2, 1]
    )

    with hotel_col1:

        hotel_name = get_value(
            selected_hotel,
            "name",
            "Selected hotel",
        )

        st.subheader(
            hotel_name
        )

        location = get_value(
            selected_hotel,
            "location",
            "",
        )

        if location:
            st.write(
                f"📍 {location}"
            )

        room_name = get_value(
            selected_hotel,
            "room_name",
            "",
        )

        if room_name:
            st.write(
                f"🛏️ {room_name}"
            )

        board = get_value(
            selected_hotel,
            "board",
            "",
        )

        if board:
            st.write(
                f"🍽️ {board}"
            )

        check_in = get_value(
            selected_hotel,
            "check_in_date",
            "",
        )

        check_out = get_value(
            selected_hotel,
            "check_out_date",
            "",
        )

        if check_in and check_out:

            st.write(
                f"📅 {format_date(check_in)} "
                f"→ "
                f"{format_date(check_out)}"
            )

    with hotel_col2:

        hotel_price = get_value(
            selected_hotel,
            "total_price_inr",
            0,
        )

        st.metric(
            "Total hotel cost",
            format_inr(hotel_price),
        )

        free_cancellation = get_value(
            selected_hotel,
            "free_cancellation",
            False,
        )

        if free_cancellation:

            st.success(
                "Free cancellation"
            )

        else:

            st.warning(
                "Cancellation restrictions apply"
            )

else:

    st.warning(
        "No hotel was selected."
    )


st.divider()


# ============================================================
# BUDGET
# ============================================================

st.header("💰 Estimated Trip Cost")

if budget:

    total_cost = get_value(
        budget,
        "total_cost",
        0,
    )

    st.metric(
        "Estimated total",
        format_inr(total_cost),
    )

    budget_col1, budget_col2, budget_col3, budget_col4, budget_col5 = (
        st.columns(5)
    )

    with budget_col1:

        st.metric(
            "Flights",
            format_inr(
                get_value(
                    budget,
                    "flight_cost",
                    0,
                )
            ),
        )

    with budget_col2:

        st.metric(
            "Hotel",
            format_inr(
                get_value(
                    budget,
                    "hotel_cost",
                    0,
                )
            ),
        )

    with budget_col3:

        st.metric(
            "Food",
            format_inr(
                get_value(
                    budget,
                    "food_cost",
                    0,
                )
            ),
        )

    with budget_col4:

        st.metric(
            "Transport",
            format_inr(
                get_value(
                    budget,
                    "transport_cost",
                    0,
                )
            ),
        )

    with budget_col5:

        st.metric(
            "Activities",
            format_inr(
                get_value(
                    budget,
                    "activity_cost",
                    0,
                )
            ),
        )

    budget_notes = get_value(
        budget,
        "notes",
        "",
    )

    if budget_notes:

        st.caption(
            budget_notes
        )

else:

    st.warning(
        "No budget estimate was generated."
    )


st.divider()


# ============================================================
# ITINERARY
# ============================================================

st.header("📅 Your Itinerary")

if itinerary:

    days = get_value(
        itinerary,
        "days",
        [],
    )

    if days:

        for day in days:

            day_number = get_value(
                day,
                "day",
                "",
            )

            day_date = get_value(
                day,
                "date",
                "",
            )

            day_area = get_value(
                day,
                "area",
                "",
            )

            title = (
                f"Day {day_number} • "
                f"{format_date(day_date)}"
            )

            with st.container(
                border=True
            ):

                st.subheader(
                    title
                )

                if day_area:

                    st.caption(
                        f"📍 {day_area}"
                    )

                activities = get_value(
                    day,
                    "activities",
                    [],
                )

                if not activities:

                    st.info(
                        "No activities scheduled."
                    )

                else:

                    for activity in activities:

                        start_time = get_value(
                            activity,
                            "start_time",
                            "",
                        )

                        end_time = get_value(
                            activity,
                            "end_time",
                            "",
                        )

                        activity_name = get_value(
                            activity,
                            "name",
                            "Activity",
                        )

                        location = get_value(
                            activity,
                            "location",
                            "",
                        )

                        description = get_value(
                            activity,
                            "description",
                            "",
                        )

                        cost = get_value(
                            activity,
                            "estimated_cost",
                            0,
                        )

                        activity_currency = get_value(
                            activity,
                            "currency",
                            "INR",
                        )

                        # ------------------------------------
                        # ACTIVITY
                        # ------------------------------------

                        activity_col1, activity_col2 = (
                            st.columns([1, 4])
                        )

                        with activity_col1:

                            st.markdown(
                                f"**{start_time}**"
                            )

                            st.caption(
                                f"to {end_time}"
                            )

                        with activity_col2:

                            st.markdown(
                                f"**{activity_name}**"
                            )

                            if location:

                                st.caption(
                                    f"📍 {location}"
                                )

                            if description:

                                st.write(
                                    description
                                )

                            if activity_currency.upper() == "INR":

                                if float(cost or 0) > 0:

                                    st.caption(
                                        f"Estimated cost: "
                                        f"{format_inr(cost)}"
                                    )

                        st.divider()

    else:

        st.warning(
            "No itinerary days were generated."
        )

else:

    st.warning(
        "No itinerary was generated."
    )


st.divider()


# ============================================================
# DESTINATION HIGHLIGHTS
# ============================================================

if destination_research:

    st.header("🌍 Destination Highlights")

    highlight_col1, highlight_col2 = (
        st.columns(2)
    )

    neighborhoods = get_value(
        destination_research,
        "neighborhoods",
        [],
    )

    must_see = get_value(
        destination_research,
        "must_see",
        [],
    )

    food = get_value(
        destination_research,
        "food",
        [],
    )

    local_transport = get_value(
        destination_research,
        "local_transport",
        [],
    )

    with highlight_col1:

        if must_see:

            st.subheader(
                "🏛️ Places to Visit"
            )

            for item in must_see:

                st.write(
                    f"• {item}"
                )

        if neighborhoods:

            st.subheader(
                "📍 Areas"
            )

            for item in neighborhoods:

                st.write(
                    f"• {item}"
                )

    with highlight_col2:

        if food:

            st.subheader(
                "🍽️ Local Food"
            )

            for item in food:

                st.write(
                    f"• {item}"
                )

        if local_transport:

            st.subheader(
                "🚇 Getting Around"
            )

            for item in local_transport:

                st.write(
                    f"• {item}"
                )


# ============================================================
# TRAVEL NOTES
# ============================================================

if schedule_validation:

    warnings = schedule_validation.get(
        "warnings",
        [],
    )

    errors = schedule_validation.get(
        "errors",
        [],
    )

    if errors or warnings:

        st.divider()

        st.header("ℹ️ Travel Notes")

        for error in errors:

            st.error(
                str(error)
            )

        for warning in warnings:

            st.warning(
                str(warning)
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Travel Planner • Flight and hotel prices are based "
    "on the available provider data at planning time."
)