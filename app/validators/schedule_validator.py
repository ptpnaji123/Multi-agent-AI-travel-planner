from datetime import datetime, timedelta

from app.models.itinerary import Itinerary
from app.models.flight import RoundTripFlightOption
from app.models.hotel import HotelOption


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_datetime(value: str) -> datetime:
    value = value.strip()

    if value.endswith("Z"):
        value = value[:-1]

    return datetime.fromisoformat(value)


def parse_time(value: str) -> int:
    """
    Convert HH:MM into minutes from midnight.
    """

    value = value.strip()

    hour, minute = value.split(":")

    hour = int(hour)
    minute = int(minute)

    if hour < 0 or hour > 23:
        raise ValueError("Invalid hour")

    if minute < 0 or minute > 59:
        raise ValueError("Invalid minute")

    return hour * 60 + minute


def build_expected_dates(
    start_date,
    end_date,
):
    dates = []

    current = start_date

    while current <= end_date:
        dates.append(current)

        current += timedelta(days=1)

    return dates


# ============================================================
# SCHEDULE VALIDATOR
# ============================================================

def validate_schedule(
    itinerary: Itinerary,
    selected_flight: RoundTripFlightOption,
    selected_hotel: HotelOption,
) -> dict:

    errors = []
    warnings = []

    outbound = selected_flight.outbound
    return_flight = selected_flight.return_flight

    arrival_datetime = parse_datetime(
        outbound.arrival_time
    )

    departure_datetime = parse_datetime(
        return_flight.departure_time
    )

    trip_start = arrival_datetime.date()
    trip_end = departure_datetime.date()

    expected_dates = build_expected_dates(
        trip_start,
        trip_end,
    )

    # ========================================================
    # EXACT NUMBER OF DAYS
    # ========================================================

    if len(itinerary.days) != len(expected_dates):

        errors.append(
            f"Expected {len(expected_dates)} itinerary days, "
            f"but received {len(itinerary.days)}."
        )

    # ========================================================
    # EXPECTED DATE SET
    # ========================================================

    expected_date_set = set(
        expected_dates
    )

    actual_dates = set()

    for day in itinerary.days:

        try:

            day_date = datetime.strptime(
                day.date,
                "%Y-%m-%d",
            ).date()

            actual_dates.add(
                day_date
            )

        except ValueError:

            errors.append(
                f"Invalid date format for itinerary day "
                f"{day.day}: '{day.date}'. "
                f"Expected YYYY-MM-DD."
            )

    # ========================================================
    # UNEXPECTED DATES
    # ========================================================

    unexpected_dates = (
        actual_dates - expected_date_set
    )

    for date_value in unexpected_dates:

        errors.append(
            f"Itinerary contains date outside the trip: "
            f"{date_value}"
        )

    # ========================================================
    # MISSING DATES
    # ========================================================

    missing_dates = (
        expected_date_set - actual_dates
    )

    for date_value in sorted(missing_dates):

        errors.append(
            f"Itinerary is missing date: "
            f"{date_value}"
        )

    # ========================================================
    # DAY NUMBERING
    # ========================================================

    for index, day in enumerate(
        itinerary.days,
        start=1,
    ):

        if day.day != index:

            errors.append(
                f"Incorrect day number for {day.date}: "
                f"expected Day {index}, "
                f"got Day {day.day}."
            )

    # ========================================================
    # EXACT DATE ORDER
    # ========================================================

    for index, day in enumerate(
        itinerary.days,
        start=1,
    ):

        if index > len(expected_dates):
            break

        expected_date = expected_dates[index - 1]

        try:

            actual_date = datetime.strptime(
                day.date,
                "%Y-%m-%d",
            ).date()

            if actual_date != expected_date:

                errors.append(
                    f"Day {index} has date "
                    f"{actual_date}, expected "
                    f"{expected_date}."
                )

        except ValueError:
            continue

    # ========================================================
    # ARRIVAL / DEPARTURE BUFFER
    # ========================================================

    arrival_buffer_end = (
        arrival_datetime
        + timedelta(minutes=90)
    )

    airport_arrival_target = (
        departure_datetime
        - timedelta(minutes=180)
    )

    # ========================================================
    # ACTIVITY VALIDATION
    # ========================================================

    for day in itinerary.days:

        try:

            day_date = datetime.strptime(
                day.date,
                "%Y-%m-%d",
            ).date()

        except ValueError:

            continue

        activities = day.activities

        previous_end = None

        for activity in activities:

            # ------------------------------------------------
            # TIME FORMAT
            # ------------------------------------------------

            try:

                start_minutes = parse_time(
                    activity.start_time
                )

                end_minutes = parse_time(
                    activity.end_time
                )

            except Exception:

                errors.append(
                    f"Invalid time for "
                    f"'{activity.name}' on "
                    f"{day.date}: "
                    f"{activity.start_time} - "
                    f"{activity.end_time}"
                )

                continue

            # ------------------------------------------------
            # DURATION
            # ------------------------------------------------

            if end_minutes <= start_minutes:

                errors.append(
                    f"Invalid activity duration: "
                    f"'{activity.name}' on "
                    f"{day.date}."
                )

            # ------------------------------------------------
            # OVERLAP
            # ------------------------------------------------

            if (
                previous_end is not None
                and start_minutes < previous_end
            ):

                errors.append(
                    f"Overlapping activities on "
                    f"{day.date}: "
                    f"'{activity.name}' starts "
                    f"before the previous activity ends."
                )

            previous_end = end_minutes

            # ------------------------------------------------
            # CURRENCY
            # ------------------------------------------------

            if activity.currency != "INR":

                errors.append(
                    f"Activity '{activity.name}' "
                    f"on {day.date} uses currency "
                    f"'{activity.currency}'. "
                    f"Expected INR."
                )

            # ------------------------------------------------
            # ARRIVAL DAY
            # ------------------------------------------------

            if day_date == arrival_datetime.date():

                arrival_minutes = (
                    arrival_datetime.hour * 60
                    + arrival_datetime.minute
                )

                buffer_end_minutes = (
                    arrival_buffer_end.hour * 60
                    + arrival_buffer_end.minute
                )

                # System logistics may begin at arrival.
                logistics_keywords = (
                    "arrival",
                    "immigration",
                    "airport",
                    "transfer",
                    "hotel check-in",
                    "check-in",
                    "rest",
                )

                activity_name = (
                    activity.name.lower()
                )

                is_logistics = any(
                    keyword in activity_name
                    for keyword in logistics_keywords
                )

                if (
                    start_minutes < arrival_minutes
                ):

                    errors.append(
                        f"'{activity.name}' on arrival "
                        f"day {day.date} starts at "
                        f"{activity.start_time}, "
                        f"before flight arrival at "
                        f"{arrival_datetime.strftime('%H:%M')}."
                    )

                # Sightseeing should respect arrival buffer.
                if (
                    not is_logistics
                    and start_minutes < buffer_end_minutes
                ):

                    errors.append(
                        f"'{activity.name}' on arrival "
                        f"day {day.date} starts at "
                        f"{activity.start_time}, "
                        f"before the recommended arrival "
                        f"buffer ends at "
                        f"{arrival_buffer_end.strftime('%H:%M')}."
                    )

            # ------------------------------------------------
            # DEPARTURE DAY
            # ------------------------------------------------

            if day_date == departure_datetime.date():

                departure_minutes = (
                    departure_datetime.hour * 60
                    + departure_datetime.minute
                )

                airport_target_minutes = (
                    airport_arrival_target.hour * 60
                    + airport_arrival_target.minute
                )

                activity_name = (
                    activity.name.lower()
                )

                airport_keywords = (
                    "airport",
                    "checkout",
                    "check-out",
                    "transfer",
                )

                is_departure_logistics = any(
                    keyword in activity_name
                    for keyword in airport_keywords
                )

                if start_minutes >= departure_minutes:

                    errors.append(
                        f"'{activity.name}' on departure "
                        f"day {day.date} starts at "
                        f"{activity.start_time}, "
                        f"after the return flight departure "
                        f"at "
                        f"{departure_datetime.strftime('%H:%M')}."
                    )

                if end_minutes > departure_minutes:

                    errors.append(
                        f"'{activity.name}' on departure "
                        f"day {day.date} ends at "
                        f"{activity.end_time}, "
                        f"after the return flight departure "
                        f"at "
                        f"{departure_datetime.strftime('%H:%M')}."
                    )

                # Any airport/transfer activity should
                # reasonably reach the airport target.
                if (
                    "airport" in activity_name
                    and start_minutes > airport_target_minutes
                ):

                    warnings.append(
                        f"'{activity.name}' starts at "
                        f"{activity.start_time}. "
                        f"Recommended airport arrival "
                        f"target is "
                        f"{airport_arrival_target.strftime('%H:%M')}."
                    )

    # ========================================================
    # HOTEL DATE VALIDATION
    # ========================================================

    try:

        hotel_check_in = datetime.strptime(
            selected_hotel.check_in_date,
            "%Y-%m-%d",
        ).date()

        hotel_check_out = datetime.strptime(
            selected_hotel.check_out_date,
            "%Y-%m-%d",
        ).date()

        if hotel_check_in < trip_start:

            errors.append(
                "Hotel check-in is before "
                "the trip starts."
            )

        if hotel_check_out > trip_end:

            errors.append(
                "Hotel check-out is after "
                "the return flight date."
            )

    except Exception:

        warnings.append(
            "Hotel dates could not be validated."
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
    }