from app.validators.schedule_validator import validate_schedule

from app.models.itinerary import (
    Itinerary,
    ItineraryDay,
    Activity,
)

from app.models.flight import (
    RoundTripFlightOption,
    FlightSegment,
)

from app.models.hotel import HotelOption


# --------------------------------------------------
# Fake flight
# --------------------------------------------------

flight = RoundTripFlightOption(
    outbound=FlightSegment(
        airline="Duffel Airways",
        flight_number="6057",
        origin="COK",
        destination="DXB",
        departure_time="2026-12-10T06:58:00",
        arrival_time="2026-12-10T09:45:00",
        duration="4h 17m",
    ),
    return_flight=FlightSegment(
        airline="Duffel Airways",
        flight_number="6058",
        origin="DXB",
        destination="COK",
        departure_time="2026-12-15T10:50:00",
        arrival_time="2026-12-15T16:37:00",
        duration="4h 47m",
    ),
    total_price=230.40,
    currency="USD",
    total_price_inr=22040.064,
    provider="Duffel",
)


# --------------------------------------------------
# Fake hotel
# --------------------------------------------------

hotel = HotelOption(
    hotel_code="TEST001",
    name="You&Co Dubai",
    location="Dubai",
    room_name="MeetUp single room in shared apartment",
    board="ROOM ONLY",
    check_in_date="2026-12-10",
    check_out_date="2026-12-15",
    price_per_night=47.222,
    total_price=236.11,
    currency="EUR",
    price_inr=25868.21,
)


# --------------------------------------------------
# Deliberately INVALID itinerary
# --------------------------------------------------

itinerary = Itinerary(
    destination="Dubai",
    days=[
        ItineraryDay(
            day=1,
            date="2026-12-10",
            area="Downtown Dubai",
            activities=[
                Activity(
                    name="Hotel Check-in",
                    start_time="11:00",
                    end_time="12:00",
                    location="You&Co Dubai",
                )
            ],
        ),

        ItineraryDay(
            day=2,
            date="2026-12-11",
            area="Downtown Dubai",
            activities=[
                Activity(
                    name="Dubai Mall",
                    start_time="10:00",
                    end_time="13:00",
                    location="Dubai Mall",
                ),
                Activity(
                    name="Burj Khalifa",
                    start_time="12:00",
                    end_time="14:00",
                    location="Burj Khalifa",
                ),
            ],
        ),

        ItineraryDay(
            day=3,
            date="2026-12-12",
            area="Jumeirah",
            activities=[],
        ),

        ItineraryDay(
            day=4,
            date="2026-12-13",
            area="Palm Jumeirah",
            activities=[],
        ),

        ItineraryDay(
            day=5,
            date="2026-12-14",
            area="Dubai",
            activities=[],
        ),

        ItineraryDay(
            day=6,
            date="2026-12-15",
            area="Dubai",
            activities=[
                Activity(
                    name="Lunch",
                    start_time="13:00",
                    end_time="14:30",
                    location="Dubai",
                )
            ],
        ),
    ],
)


# --------------------------------------------------
# Validate
# --------------------------------------------------

result = validate_schedule(
    itinerary=itinerary,
    selected_flight=flight,
    selected_hotel=hotel,
)


print("\n==============================")
print("SCHEDULE VALIDATION")
print("==============================")

print(
    f"\nValid: {result['valid']}"
)

print("\nErrors:")

for error in result["errors"]:
    print(f"- {error}")

print("\nWarnings:")

for warning in result["warnings"]:
    print(f"- {warning}")