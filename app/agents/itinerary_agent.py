from datetime import datetime, timedelta
import re

from app.llm.mistral import llm

from app.models.trip_request import TripRequest
from app.models.destination import DestinationResearch
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.budget import BudgetReport
from app.models.itinerary import Itinerary


# ============================================================
# PLANNING CONSTANTS
# ============================================================

# Planning buffer after flight arrival before normal sightseeing.
ARRIVAL_BUFFER_MINUTES = 90

# Recommended airport arrival before international departure.
AIRPORT_BUFFER_MINUTES = 180

# Planning assumption for hotel -> airport transfer.
AIRPORT_TRANSFER_MINUTES = 30

# Planning assumption for hotel checkout.
CHECKOUT_DURATION_MINUTES = 15


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_time(value: datetime) -> str:
    """Convert datetime to HH:MM."""
    return value.strftime("%H:%M")


def parse_datetime(value: str) -> datetime:
    """Parse ISO datetime from flight data."""

    value = str(value).strip()

    if value.endswith("Z"):
        value = value[:-1]

    return datetime.fromisoformat(value)


def build_trip_dates(
    start_date,
    end_date,
) -> list[str]:
    """
    Build the exact list of itinerary dates.

    Example:

    2026-12-10 -> 2026-12-15

    produces exactly 6 dates.
    """

    dates = []

    current = start_date

    while current <= end_date:

        dates.append(
            current.strftime("%Y-%m-%d")
        )

        current += timedelta(days=1)

    return dates


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_valid_date(
    raw_date: str,
) -> str | None:
    """
    Extract YYYY-MM-DD from an LLM-generated date.

    Handles:

    2026-12-10

    Arrival Day - 2026-12-10

    Day 1 - 2026-12-10
    """

    if not raw_date:
        return None

    raw_date = str(raw_date).strip()

    # Exact YYYY-MM-DD.
    try:

        parsed = datetime.strptime(
            raw_date,
            "%Y-%m-%d",
        )

        return parsed.strftime(
            "%Y-%m-%d"
        )

    except ValueError:
        pass

    # Extract date from text.
    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        raw_date,
    )

    if not match:
        return None

    candidate = match.group(0)

    try:

        parsed = datetime.strptime(
            candidate,
            "%Y-%m-%d",
        )

        return parsed.strftime(
            "%Y-%m-%d"
        )

    except ValueError:

        return None


# ============================================================
# NORMALIZE ITINERARY
# ============================================================

def normalize_itinerary(
    itinerary: Itinerary,
    trip_request: TripRequest,
) -> Itinerary:
    """
    Deterministically normalize fields that should never
    depend on LLM behavior.

    Guarantees:

    - exact trip dates
    - exact number of days
    - sequential day numbers
    - YYYY-MM-DD dates
    - INR currency
    - missing costs become zero
    - no dates outside the trip
    """

    expected_dates = build_trip_dates(
        trip_request.start_date,
        trip_request.end_date,
    )

    normalized_days = []

    generated_by_date = {}

    # --------------------------------------------------------
    # Build date lookup
    # --------------------------------------------------------

    for day in itinerary.days:

        parsed_date = extract_valid_date(
            day.date
        )

        if parsed_date is None:
            continue

        # Only preserve dates that belong to this trip.
        if parsed_date not in expected_dates:
            continue

        generated_by_date[parsed_date] = day

    # --------------------------------------------------------
    # Build EXACT expected days
    # --------------------------------------------------------

    for index, date_value in enumerate(
        expected_dates,
        start=1,
    ):

        generated_day = generated_by_date.get(
            date_value
        )

        if generated_day is not None:

            generated_day.day = index
            generated_day.date = date_value

            # -----------------------------------------------
            # Normalize activities
            # -----------------------------------------------

            for activity in generated_day.activities:

                activity.currency = "INR"

                if activity.estimated_cost is None:
                    activity.estimated_cost = 0.0

                # Normalize whitespace.
                activity.name = (
                    activity.name.strip()
                )

                activity.location = (
                    activity.location.strip()
                )

        else:

            # Create empty day rather than inventing content.
            generated_day = {
                "day": index,
                "date": date_value,
                "area": "",
                "activities": [],
            }

        normalized_days.append(
            generated_day
        )

    # --------------------------------------------------------
    # Replace itinerary days
    # --------------------------------------------------------

    itinerary.days = normalized_days

    return itinerary


# ============================================================
# MAIN ITINERARY AGENT
# ============================================================

def itinerary_agent(
    trip_request: TripRequest,
    destination_research: DestinationResearch,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
    budget_report: BudgetReport,
) -> Itinerary:

    structured_llm = llm.with_structured_output(
        Itinerary
    )

    # ========================================================
    # TRIP DATES
    # ========================================================

    start_date = trip_request.start_date
    end_date = trip_request.end_date

    expected_dates = build_trip_dates(
        start_date,
        end_date,
    )

    calendar_days = len(
        expected_dates
    )

    # ========================================================
    # FLIGHT TIMES
    # ========================================================

    outbound = selected_flight.outbound
    return_flight = selected_flight.return_flight

    arrival_datetime = parse_datetime(
        outbound.arrival_time
    )

    departure_datetime = parse_datetime(
        return_flight.departure_time
    )

    # ========================================================
    # ARRIVAL BUFFER
    # ========================================================

    earliest_usable_time = (
        arrival_datetime
        + timedelta(
            minutes=ARRIVAL_BUFFER_MINUTES
        )
    )

    # ========================================================
    # DEPARTURE BUFFER
    # ========================================================

    target_airport_arrival = (
        departure_datetime
        - timedelta(
            minutes=AIRPORT_BUFFER_MINUTES
        )
    )

    hotel_departure_time = (
        target_airport_arrival
        - timedelta(
            minutes=AIRPORT_TRANSFER_MINUTES
        )
    )

    hotel_checkout_time = (
        hotel_departure_time
        - timedelta(
            minutes=CHECKOUT_DURATION_MINUTES
        )
    )

    # ========================================================
    # DESTINATION RESEARCH
    # ========================================================

    neighborhoods = (
        destination_research.neighborhoods
    )

    must_see = (
        destination_research.must_see
    )

    food = (
        destination_research.food
    )

    transport = (
        destination_research.local_transport
    )

    # ========================================================
    # HOTEL
    # ========================================================

    hotel_name = selected_hotel.name
    hotel_room = selected_hotel.room_name
    hotel_board = selected_hotel.board

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are the itinerary planning agent in a multi-agent
travel planning system.

Your job is to create a practical day-by-day itinerary.

The output MUST be a structured Itinerary matching the
supplied Pydantic schema.

============================================================
TRIP
============================================================

Origin:
{trip_request.origin}

Destination:
{trip_request.destination}

Travelers:
{trip_request.travelers}

Start date:
{start_date}

End date:
{end_date}

Pace:
{trip_request.pace}

Interests:
{trip_request.interests}

============================================================
ABSOLUTE DATE RULES
============================================================

The exact trip dates are:

{expected_dates}

There are EXACTLY:

{calendar_days}

calendar days.

You MUST return exactly:

{calendar_days}

ItineraryDay objects.

The dates MUST be exactly:

{expected_dates}

DO NOT:

- add another day
- remove a day
- create a date before the trip
- create a date after the trip
- create 2026-12-16
- create dates outside the supplied list

The date field MUST contain only:

YYYY-MM-DD

Examples:

2026-12-10
2026-12-11
2026-12-12

Do NOT use:

Arrival Day - 2026-12-10
Day 1 - 2026-12-10
20261210

============================================================
DAY NUMBER RULES
============================================================

Day numbers MUST be sequential.

For this trip:

Day 1 = 2026-12-10
Day 2 = 2026-12-11
Day 3 = 2026-12-12
Day 4 = 2026-12-13
Day 5 = 2026-12-14
Day 6 = 2026-12-15

Never use dates as day numbers.

============================================================
TIME RULES
============================================================

Every activity MUST contain:

start_time = HH:MM
end_time = HH:MM

Use 24-hour time.

Valid:

09:00
10:30
17:45

Invalid:

Morning
Evening
Upon arrival
After arrival
Departure time
Approx. 1 hour

============================================================
ARRIVAL DAY
============================================================

Outbound flight:

Airline:
{outbound.airline}

Flight:
{outbound.flight_number}

Origin:
{outbound.origin}

Destination:
{outbound.destination}

Departure:
{outbound.departure_time}

Arrival:
{outbound.arrival_time}

Recommended earliest usable itinerary time:

{format_time(earliest_usable_time)}

This is a planning buffer of:

{ARRIVAL_BUFFER_MINUTES}

minutes after flight arrival.

Therefore:

Do NOT schedule sightseeing before:

{format_time(earliest_usable_time)}

Arrival-day activities may include:

- Airport arrival / immigration
- Airport transfer
- Hotel check-in
- Rest

These are SYSTEM LOGISTICS and are allowed.

Do NOT add sightseeing immediately after landing.

============================================================
DEPARTURE DAY
============================================================

Return flight:

Airline:
{return_flight.airline}

Flight:
{return_flight.flight_number}

Departure:
{return_flight.departure_time}

Arrival:
{return_flight.arrival_time}

Recommended airport arrival target:

{format_time(target_airport_arrival)}

Recommended hotel departure:

{format_time(hotel_departure_time)}

Recommended hotel checkout:

{format_time(hotel_checkout_time)}

Departure-day activities may include:

- Hotel checkout
- Airport transfer
- Airport check-in
- Airport security
- Departure procedures

Do NOT schedule sightseeing on the departure day.

Do NOT schedule lunch or dinner after airport departure preparation.

Do NOT create ANY activity after:

{return_flight.departure_time}

============================================================
SUPPORTED DESTINATION CONTENT
============================================================

You MUST use the supplied destination research.

Neighborhoods:

{neighborhoods}

Supported attractions:

{must_see}

Supported local food:

{food}

Supported transportation:

{transport}

============================================================
ATTRACTION RULE
============================================================

For sightseeing activities, use ONLY attractions from:

{must_see}

Do NOT invent additional tourist attractions.

Do NOT add attractions such as:

Motiongate
Bollywood Parks
Legoland
Jumeirah Beach
Dubai Museum
Al Fahidi Historic District
Gold Souk
Dubai Fountain
Wild Wadi
VR Park
Dubai Marina Yacht Club

unless they explicitly appear in the supplied research.

If there are not enough attractions:

- reuse a supported attraction
- use rest/free time
- use a meal
- use a transportation activity

Do NOT invent a new attraction.

============================================================
FOOD RULE
============================================================

Do NOT invent restaurant names.

Do NOT create named restaurants unless they are present
in the supplied research.

Use generic meal activities such as:

Breakfast
Lunch
Dinner
Local food experience

Possible supported food:

{food}

============================================================
NEIGHBORHOOD RULE
============================================================

Only use neighborhood names from:

{neighborhoods}

Do not invent neighborhood names.

============================================================
ACTIVITY COST RULE
============================================================

Currency MUST always be:

INR

If no reliable activity price is available:

estimated_cost = 0

Do NOT invent precise prices.

============================================================
TRAVEL-TIME RULE
============================================================

Do not invent precise travel times between attractions.

Leave reasonable gaps between activities.

This itinerary is a planning estimate.

It is NOT a booking confirmation.

============================================================
HOTEL
============================================================

Hotel:

{hotel_name}

Room:

{hotel_room}

Board:

{hotel_board}

Check-in:

{selected_hotel.check_in_date}

Check-out:

{selected_hotel.check_out_date}

============================================================
BUDGET
============================================================

Estimated total:

₹{budget_report.total_cost:,.2f}

============================================================
ITINERARY DESIGN
============================================================

ARRIVAL DAY:

Keep the day light.

Use:

Airport arrival / immigration
Airport transfer
Hotel check-in
Rest

FULL DAYS:

Use supported attractions.

Group attractions by neighborhood where possible.

Do not overcrowd the day.

Include meals and breaks.

DEPARTURE DAY:

Keep the day light.

Use:

Hotel checkout
Airport transfer
Airport check-in/security

Do not include sightseeing.

============================================================
FINAL HARD REQUIREMENTS
============================================================

Return exactly:

{calendar_days}

days.

The final date MUST be:

{end_date.strftime("%Y-%m-%d")}

The itinerary MUST NOT contain:

{(end_date + timedelta(days=1)).strftime("%Y-%m-%d")}

All activities must use:

currency = INR

Return ONLY the structured Itinerary.
"""

    # ========================================================
    # CALL MISTRAL
    # ========================================================

    print(
        "\nGenerating itinerary with Mistral..."
    )

    itinerary = structured_llm.invoke(
        prompt
    )

    # ========================================================
    # DETERMINISTIC NORMALIZATION
    # ========================================================

    itinerary = normalize_itinerary(
        itinerary,
        trip_request,
    )

    # ========================================================
    # PRINT RESULT
    # ========================================================

    print(
        "\n--- ITINERARY GENERATED ---"
    )

    print(
        f"Destination: "
        f"{itinerary.destination}"
    )

    print(
        f"Days generated: "
        f"{len(itinerary.days)}"
    )

    for day in itinerary.days:

        print(
            f"\nDay {day.day} "
            f"({day.date})"
        )

        print(
            f"Area: {day.area}"
        )

        for activity in day.activities:

            print(
                f"  "
                f"{activity.start_time} - "
                f"{activity.end_time}: "
                f"{activity.name}"
            )

            print(
                f"  Location: "
                f"{activity.location}"
            )

            print(
                f"  Cost: "
                f"₹{activity.estimated_cost:,.2f}"
            )

            print(
                f"  Currency: "
                f"{activity.currency}"
            )

    return itinerary