from datetime import datetime, timedelta

from app.models.itinerary import (
    Itinerary,
    ItineraryDay,
    Activity,
)
from app.models.trip_request import TripRequest
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption


def _parse_datetime(value: str) -> datetime:
    """
    Parse common ISO flight datetime formats.
    """

    value = value.strip()

    if value.endswith("Z"):
        value = value[:-1]

    # Handle timezone offset if present.
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    # Fallback formats.
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Unable to parse flight datetime: {value}"
    )


def _minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _time(minutes: int) -> str:
    minutes = max(0, min(minutes, 23 * 60 + 59))

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


def _make_activity(
    name: str,
    start: int,
    end: int,
    location: str,
    description: str = "",
    cost: float = 0.0,
) -> Activity:

    return Activity(
        name=name,
        start_time=_time(start),
        end_time=_time(end),
        location=location,
        description=description,
        estimated_cost=cost,
        currency="INR",
    )


def _arrival_day(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> ItineraryDay:

    arrival_dt = _parse_datetime(
        selected_flight.outbound.arrival_time
    )

    arrival = arrival_dt.hour * 60 + arrival_dt.minute

    # 60 minutes for immigration/arrival processing.
    immigration_end = arrival + 60

    # 30 minutes transfer to hotel.
    transfer_end = immigration_end + 30

    # Hotel check-in starts after the 90-minute arrival buffer.
    checkin_end = transfer_end + 45

    rest_end = min(checkin_end + 180, 22 * 60)

    activities = [
        _make_activity(
            name="Airport Arrival & Immigration",
            start=arrival,
            end=immigration_end,
            location="DXB",
            description="Arrival, immigration and baggage collection.",
            cost=0,
        ),
        _make_activity(
            name="Airport Transfer",
            start=immigration_end,
            end=transfer_end,
            location=selected_hotel.hotel_name,
            description="Transfer from Dubai International Airport to the hotel.",
            cost=0,
        ),
        _make_activity(
            name="Hotel Check-in",
            start=transfer_end,
            end=checkin_end,
            location=selected_hotel.hotel_name,
            description="Hotel check-in and settling into the room.",
            cost=0,
        ),
        _make_activity(
            name="Rest",
            start=checkin_end,
            end=rest_end,
            location=selected_hotel.hotel_name,
            description="Rest after the journey.",
            cost=0,
        ),
    ]

    return ItineraryDay(
        day=1,
        date=trip_request.start_date.isoformat(),
        area="DXB",
        activities=activities,
    )


def _departure_day(
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> ItineraryDay:

    departure_dt = _parse_datetime(
        selected_flight.return_flight.departure_time
    )

    departure = departure_dt.hour * 60 + departure_dt.minute

    # 3 hours before flight departure.
    airport_target = departure - 180

    # Keep hotel checkout 30 minutes before airport transfer.
    checkout_start = max(0, airport_target - 30)
    checkout_end = airport_target

    # Airport check-in/security.
    airport_end = max(
        airport_target + 150,
        departure - 30,
    )

    # Never exceed flight departure.
    airport_end = min(
        airport_end,
        departure - 5,
    )

    activities = [
        _make_activity(
            name="Hotel Checkout",
            start=checkout_start,
            end=checkout_end,
            location=selected_hotel.hotel_name,
            description="Check out from the hotel.",
            cost=0,
        ),
        _make_activity(
            name="Airport Transfer",
            start=checkout_end,
            end=airport_target,
            location="DXB",
            description="Transfer to Dubai International Airport.",
            cost=0,
        ),
        _make_activity(
            name="Airport Check-in & Security",
            start=airport_target,
            end=airport_end,
            location="DXB",
            description="Airport check-in, security and departure preparation.",
            cost=0,
        ),
    ]

    return ItineraryDay(
        day=(
            trip_request.end_date - trip_request.start_date
        ).days + 1,
        date=trip_request.end_date.isoformat(),
        area="DXB",
        activities=activities,
    )


def _clean_middle_day(day: ItineraryDay) -> ItineraryDay:

    valid_activities = []

    for activity in day.activities:

        try:
            start = _minutes(activity.start_time)
            end = _minutes(activity.end_time)
        except Exception:
            continue

        if end <= start:
            continue

        valid_activities.append(activity)

    # Sort activities.
    valid_activities.sort(
        key=lambda item: _minutes(item.start_time)
    )

    # Remove overlaps instead of inventing new activities.
    cleaned = []
    previous_end = None

    for activity in valid_activities:

        start = _minutes(activity.start_time)
        end = _minutes(activity.end_time)

        if previous_end is not None and start < previous_end:
            # Completely overlapping activity.
            if end <= previous_end:
                continue

            # Shift its start to previous end.
            start = previous_end

            if start >= end:
                continue

            activity.start_time = _time(start)

        cleaned.append(activity)
        previous_end = _minutes(activity.end_time)

    # Keep itinerary practical.
    cleaned = cleaned[:4]

    day.activities = cleaned

    return day


def deterministic_repair_itinerary(
    itinerary: Itinerary,
    trip_request: TripRequest,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> Itinerary:

    print("\n--- DETERMINISTIC ITINERARY REPAIR ---")
    print("Repairing itinerary with Python rules.")
    print("Mistral will NOT regenerate the itinerary.")

    expected_days = (
        trip_request.end_date - trip_request.start_date
    ).days + 1

    repaired_days = []

    for index in range(expected_days):

        current_date = (
            trip_request.start_date
            + timedelta(days=index)
        )

        # Arrival day.
        if index == 0:
            repaired_days.append(
                _arrival_day(
                    trip_request,
                    selected_flight,
                    selected_hotel,
                )
            )
            continue

        # Departure day.
        if index == expected_days - 1:
            repaired_days.append(
                _departure_day(
                    trip_request,
                    selected_flight,
                    selected_hotel,
                )
            )
            continue

        # Middle day.
        matching_day = None

        for day in itinerary.days:
            if day.date == current_date.isoformat():
                matching_day = day
                break

        if matching_day is None:
            matching_day = ItineraryDay(
                day=index + 1,
                date=current_date.isoformat(),
                area=trip_request.destination,
                activities=[],
            )

        matching_day.day = index + 1
        matching_day.date = current_date.isoformat()

        matching_day = _clean_middle_day(
            matching_day
        )

        repaired_days.append(matching_day)

    repaired = Itinerary(
        destination=trip_request.destination,
        days=repaired_days,
    )

    print(
        f"Deterministic repair produced "
        f"{len(repaired.days)} days."
    )

    return repaired