from datetime import datetime, timedelta

from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption
from app.models.itinerary import Activity, Itinerary, ItineraryDay


def _parse_datetime(value: str) -> datetime:
    """
    Parse a flight datetime string.

    Supports common ISO-8601 formats including:
    - 2026-12-15T10:50:00
    - 2026-12-15T10:50:00+04:00
    - 2026-12-15T10:50
    """

    value = value.strip()

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    return datetime.fromisoformat(value)


def _format_time(value: datetime) -> str:
    return value.strftime("%H:%M")


def _format_date(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def _make_activity(
    name: str,
    start: datetime,
    end: datetime,
    location: str,
    description: str = "",
    estimated_cost: float = 0.0,
) -> Activity:

    return Activity(
        name=name,
        start_time=_format_time(start),
        end_time=_format_time(end),
        location=location,
        description=description,
        estimated_cost=estimated_cost,
        currency="INR",
    )


def _arrival_day(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> ItineraryDay:

    arrival = _parse_datetime(
        selected_flight.outbound.arrival_time
    )

    hotel_name = selected_hotel.name

    # Arrival buffer:
    # Flight arrival
    # + 60 min immigration/baggage
    # + 30 min transfer
    # + 30 min hotel check-in
    # + rest
    immigration_end = arrival + timedelta(minutes=60)
    transfer_end = immigration_end + timedelta(minutes=30)
    checkin_end = transfer_end + timedelta(minutes=30)

    rest_end = checkin_end + timedelta(hours=4)

    activities = [
        _make_activity(
            name="Arrival at Dubai International Airport",
            start=arrival,
            end=immigration_end,
            location="Dubai International Airport",
            description="Arrival, immigration and baggage collection.",
        ),
        _make_activity(
            name="Airport transfer to hotel",
            start=immigration_end,
            end=transfer_end,
            location=f"Dubai International Airport to {hotel_name}",
            description="Transfer from the airport to the selected hotel.",
        ),
        _make_activity(
            name="Hotel check-in",
            start=transfer_end,
            end=checkin_end,
            location=hotel_name,
            description="Check-in at the selected hotel.",
        ),
        _make_activity(
            name="Rest",
            start=checkin_end,
            end=rest_end,
            location=hotel_name,
            description="Rest after the journey.",
        ),
    ]

    return ItineraryDay(
        day=1,
        date=_format_date(arrival),
        area="Airport",
        activities=activities,
    )


def _departure_day(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> ItineraryDay:

    departure = _parse_datetime(
        selected_flight.return_flight.departure_time
    )

    hotel_name = selected_hotel.name

    # Target airport arrival:
    # 3 hours before international flight.
    airport_arrival_target = departure - timedelta(
        hours=3
    )

    # Assume 45 minutes for hotel -> airport transfer.
    transfer_start = airport_arrival_target - timedelta(
        minutes=45
    )

    # Hotel checkout 30 minutes before transfer.
    checkout_start = transfer_start - timedelta(
        minutes=30
    )

    checkout_end = transfer_start

    # Make sure all times remain on the departure date.
    day_start = departure.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    # If the calculated checkout time is before midnight,
    # keep it at the calculated time.
    # For a normal morning departure this will still be
    # on the same date.
    activities = []

    activities.append(
        _make_activity(
            name="Checkout from hotel",
            start=checkout_start,
            end=checkout_end,
            location=hotel_name,
            description="Check out from the selected hotel before heading to the airport.",
        )
    )

    activities.append(
        _make_activity(
            name="Airport transfer",
            start=transfer_start,
            end=airport_arrival_target,
            location=f"{hotel_name} to Dubai International Airport",
            description="Transfer to Dubai International Airport.",
        )
    )

    # Do NOT create an activity after the flight departure.
    #
    # The flight itself is handled by the selected flight object.
    # Therefore the itinerary ends at the airport arrival target.

    return ItineraryDay(
        day=1,
        date=_format_date(departure),
        area="Airport",
        activities=activities,
    )


def _clean_middle_day(
    day: ItineraryDay,
) -> ItineraryDay:

    cleaned = []

    for activity in day.activities:

        try:
            start = datetime.strptime(
                activity.start_time,
                "%H:%M",
            )

            end = datetime.strptime(
                activity.end_time,
                "%H:%M",
            )

        except ValueError:
            continue

        if end <= start:
            continue

        cleaned.append(activity)

    # Sort chronologically.
    cleaned.sort(
        key=lambda activity: datetime.strptime(
            activity.start_time,
            "%H:%M",
        )
    )

    # Remove overlapping activities.
    result = []
    previous_end = None

    for activity in cleaned:

        start = datetime.strptime(
            activity.start_time,
            "%H:%M",
        )

        end = datetime.strptime(
            activity.end_time,
            "%H:%M",
        )

        if previous_end is not None and start < previous_end:
            continue

        result.append(activity)
        previous_end = end

    # Keep the itinerary manageable.
    result = result[:5]

    return ItineraryDay(
        day=day.day,
        date=day.date,
        area=day.area,
        activities=result,
    )


def deterministic_repair_itinerary(
    trip_request: TripRequest,
    itinerary: Itinerary,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> Itinerary:

    print()
    print("--- DETERMINISTIC ITINERARY REPAIR ---")
    print("Repairing itinerary with Python rules.")
    print("Mistral will NOT regenerate the itinerary.")

    arrival = _parse_datetime(
        selected_flight.outbound.arrival_time
    )

    departure = _parse_datetime(
        selected_flight.return_flight.departure_time
    )

    expected_dates = []

    current_date = arrival.date()

    while current_date <= departure.date():
        expected_dates.append(current_date)
        current_date += timedelta(days=1)

    repaired_days = []

    total_days = len(expected_dates)

    for index, current_date in enumerate(expected_dates):

        day_number = index + 1

        # ---------------------------------------------------------
        # ARRIVAL DAY
        # ---------------------------------------------------------

        if index == 0:

            repaired_day = _arrival_day(
                trip_request=trip_request,
                selected_flight=selected_flight,
                selected_hotel=selected_hotel,
            )

            repaired_day.day = day_number
            repaired_day.date = current_date.isoformat()

            repaired_days.append(
                repaired_day
            )

            continue

        # ---------------------------------------------------------
        # DEPARTURE DAY
        # ---------------------------------------------------------

        if index == total_days - 1:

            repaired_day = _departure_day(
                trip_request=trip_request,
                selected_flight=selected_flight,
                selected_hotel=selected_hotel,
            )

            repaired_day.day = day_number
            repaired_day.date = current_date.isoformat()

            repaired_days.append(
                repaired_day
            )

            continue

        # ---------------------------------------------------------
        # MIDDLE DAYS
        # ---------------------------------------------------------

        original_day = None

        for day in itinerary.days:

            if day.date == current_date.isoformat():
                original_day = day
                break

        if original_day is None:

            # If the LLM failed to generate this date,
            # create an empty but valid day.
            repaired_day = ItineraryDay(
                day=day_number,
                date=current_date.isoformat(),
                area=trip_request.destination,
                activities=[],
            )

        else:

            repaired_day = _clean_middle_day(
                original_day
            )

            repaired_day.day = day_number
            repaired_day.date = current_date.isoformat()

        repaired_days.append(
            repaired_day
        )

    return Itinerary(
        destination=itinerary.destination,
        days=repaired_days,
    )