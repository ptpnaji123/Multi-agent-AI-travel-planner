from app.models.itinerary import Itinerary
from app.models.destination import DestinationResearch
from app.models.trip_request import TripRequest


# ============================================================
# SYSTEM ACTIVITIES
# ============================================================

SYSTEM_ACTIVITY_KEYWORDS = (
    "airport",
    "immigration",
    "hotel check-in",
    "hotel checkout",
    "hotel check-out",
    "transfer to airport",
    "airport transfer",
    "transfer",
    "rest",
    "check-in",
    "check-out",
    "breakfast",
    "lunch",
    "dinner",
    "meal",
    "food",
)


# ============================================================
# SYSTEM ACTIVITY CHECK
# ============================================================

def is_system_activity(
    activity_name: str,
) -> bool:

    name = (
        activity_name
        .lower()
        .strip()
    )

    return any(
        keyword in name
        for keyword in SYSTEM_ACTIVITY_KEYWORDS
    )


# ============================================================
# NORMALIZE ACTIVITY NAME
# ============================================================

def normalize_name(
    value: str,
) -> str:

    value = (
        value
        .lower()
        .strip()
    )

    prefixes = (
        "visit ",
        "explore ",
        "see ",
        "enjoy ",
        "relax at ",
        "experience ",
        "discover ",
    )

    for prefix in prefixes:

        if value.startswith(prefix):

            value = value[
                len(prefix):
            ]

    return value.strip()


# ============================================================
# SUPPORTED ACTIVITY CHECK
# ============================================================

def is_supported_activity(
    activity_name: str,
    destination_research: DestinationResearch,
) -> bool:

    # System activities are always allowed.
    if is_system_activity(
        activity_name
    ):
        return True

    normalized_activity = normalize_name(
        activity_name
    )

    supported_items = []

    supported_items.extend(
        destination_research.must_see
    )

    supported_items.extend(
        destination_research.neighborhoods
    )

    supported_items.extend(
        destination_research.food
    )

    for item in supported_items:

        normalized_item = normalize_name(
            item
        )

        # Exact match.
        if (
            normalized_activity
            == normalized_item
        ):
            return True

        # Supported item contained in activity.
        if (
            normalized_item
            in normalized_activity
        ):
            return True

        # Activity contained in supported item.
        if (
            normalized_activity
            in normalized_item
        ):
            return True

    return False


# ============================================================
# CRITIC
# ============================================================

def critic_agent(
    trip_request: TripRequest,
    itinerary: Itinerary,
    destination_research: DestinationResearch,
    schedule_validation: dict,
    repair_attempt: int = 0,
) -> dict:

    """
    Critic for the itinerary.

    IMPORTANT ARCHITECTURE:

    - Schedule validation errors are HARD errors.
    - Unsupported destination activities are WARNINGS.
    - The critic does NOT regenerate the itinerary.
    - Deterministic Python repair handles hard schedule problems.
    """

    errors = []
    warnings = []

    # ========================================================
    # SCHEDULE VALIDATION
    # ========================================================

    schedule_errors = schedule_validation.get(
        "errors",
        [],
    )

    schedule_warnings = schedule_validation.get(
        "warnings",
        [],
    )

    errors.extend(
        schedule_errors
    )

    warnings.extend(
        schedule_warnings
    )

    # ========================================================
    # EXACT TRIP-DAY VALIDATION
    # ========================================================

    expected_days = (
        trip_request.end_date
        - trip_request.start_date
    ).days + 1

    if len(itinerary.days) != expected_days:

        errors.append(
            "Expected "
            f"{expected_days} itinerary days, "
            f"but received "
            f"{len(itinerary.days)}."
        )

    # ========================================================
    # DATE VALIDATION
    # ========================================================

    expected_dates = []

    current_date = (
        trip_request.start_date
    )

    while current_date <= (
        trip_request.end_date
    ):

        expected_dates.append(
            current_date.isoformat()
        )

        current_date += (
            __import__("datetime").timedelta(
                days=1
            )
        )

    actual_dates = [
        day.date
        for day in itinerary.days
    ]

    if actual_dates != expected_dates:

        errors.append(
            "Itinerary dates do not exactly "
            "match the requested trip dates."
        )

    # ========================================================
    # DAY NUMBER VALIDATION
    # ========================================================

    expected_day_numbers = list(
        range(
            1,
            expected_days + 1,
        )
    )

    actual_day_numbers = [
        day.day
        for day in itinerary.days
    ]

    if (
        actual_day_numbers
        != expected_day_numbers
    ):

        errors.append(
            "Itinerary day numbers are not "
            "sequential."
        )

    # ========================================================
    # ACTIVITY SUPPORT CHECK
    # ========================================================

    unsupported_count = 0

    for day in itinerary.days:

        for activity in day.activities:

            supported = is_supported_activity(
                activity.name,
                destination_research,
            )

            if not supported:

                unsupported_count += 1

                # IMPORTANT:
                # This is only a warning.
                #
                # Destination research is not a closed-world
                # database. An attraction may exist even if
                # it was not returned in the research list.

                warnings.append(
                    f"Activity "
                    f"'{activity.name}' on "
                    f"{day.date} was not directly "
                    f"found in the supplied "
                    f"destination research."
                )

    # ========================================================
    # COST CHECK
    # ========================================================

    total_activities = 0

    zero_cost_activities = 0

    for day in itinerary.days:

        for activity in day.activities:

            total_activities += 1

            if (
                activity.estimated_cost
                == 0
            ):

                zero_cost_activities += 1

    if (
        total_activities > 0
        and zero_cost_activities
        == total_activities
    ):

        warnings.append(
            "All itinerary activities have "
            "zero estimated cost. Activity "
            "pricing should be enriched later "
            "using live activity-price data."
        )

    # ========================================================
    # REPAIR STATUS
    # ========================================================

    valid = len(errors) == 0

    needs_repair = not valid

    # ========================================================
    # PRINT
    # ========================================================

    print(
        "\nCritic Result:"
    )

    print(
        f"Valid: {valid}"
    )

    if errors:

        print(
            "\nErrors:"
        )

        for error in errors:

            print(
                f"- {error}"
            )

    if warnings:

        print(
            "\nWarnings:"
        )

        for warning in warnings:

            print(
                f"- {warning}"
            )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "valid": valid,
        "needs_repair": needs_repair,
        "errors": errors,
        "warnings": warnings,
        "unsupported_activity_count": (
            unsupported_count
        ),
        "repair_attempt": repair_attempt,
    }