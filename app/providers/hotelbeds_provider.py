from datetime import date

import requests

from app.config import HOTELBEDS_API_KEY

from app.models.hotel import (
    CancellationPolicy,
    HotelOption,
)

from app.providers.hotelbeds_auth import (
    get_hotelbeds_headers,
)


class HotelbedsProvider:

    BASE_URL = (
        "https://api-mtls.test.hotelbeds.com"
    )

    HOTEL_API_PATH = (
        "/hotel-api/1.0/hotels"
    )

    def __init__(
        self,
        certificate_path: str,
        private_key_path: str,
    ):

        if not HOTELBEDS_API_KEY:
            raise ValueError(
                "HOTELBEDS_API_KEY is not configured."
            )

        self.certificate_path = certificate_path
        self.private_key_path = private_key_path

    def search_hotels(
        self,
        destination_code: str,
        check_in_date: date,
        check_out_date: date,
        adults: int = 1,
        rooms: int = 1,
    ) -> list[HotelOption]:

        payload = {
            "stay": {
                "checkIn": check_in_date.isoformat(),
                "checkOut": check_out_date.isoformat(),
            },

            "occupancies": [
                {
                    "rooms": rooms,
                    "adults": adults,
                    "children": 0,
                }
            ],

            "destination": {
                "code": destination_code,
            },

            "dailyRate": True,
        }

        headers = get_hotelbeds_headers()

        response = requests.post(
            self.BASE_URL + self.HOTEL_API_PATH,
            headers=headers,
            json=payload,
            cert=(
                self.certificate_path,
                self.private_key_path,
            ),
            timeout=60,
        )

        print(
            "\n--- HOTELBEDS HOTEL SEARCH ---"
        )

        print(
            "Status:",
            response.status_code,
        )

        if not response.ok:

            print(
                "\nResponse:"
            )

            print(
                response.text
            )

            response.raise_for_status()

        data = response.json()

        return self._parse_hotels(
            data=data,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )

    def _parse_hotels(
        self,
        data: dict,
        check_in_date: date,
        check_out_date: date,
    ) -> list[HotelOption]:

        results = []

        hotels_data = (
            data
            .get("hotels", {})
            .get("hotels", [])
        )

        number_of_nights = (
            check_out_date - check_in_date
        ).days

        for hotel in hotels_data:

            hotel_code = str(
                hotel.get(
                    "code",
                    "",
                )
            )

            hotel_name = hotel.get(
                "name",
                "",
            )

            category = hotel.get(
                "categoryName",
                "",
            )

            destination = hotel.get(
                "destinationName",
                "",
            )

            # Hotelbeds provides the currency
            # for the hotel rates at hotel level.
            #
            # Example from the actual response:
            #
            # "currency": "EUR"
            #
            # This is the currency that should
            # be associated with the hotel's
            # "net" price.

            hotel_currency = hotel.get(
                "currency",
                "",
            )

            rooms = hotel.get(
                "rooms",
                [],
            )

            for room in rooms:

                room_code = room.get(
                    "code",
                    "",
                )

                room_name = room.get(
                    "name",
                    "",
                )

                rates = room.get(
                    "rates",
                    [],
                )

                for rate in rates:

                    total_price = self._get_price(
                        rate
                    )

                    price_per_night = (
                        total_price / number_of_nights
                        if number_of_nights > 0
                        else total_price
                    )

                    currency = (
                        hotel_currency
                        or self._get_rate_currency(
                            rate
                        )
                    )

                    board = rate.get(
                        "boardName",
                        "",
                    )

                    rate_key = rate.get(
                        "rateKey",
                        "",
                    )

                    rate_type = rate.get(
                        "rateType",
                        "",
                    )

                    rate_class = rate.get(
                        "rateClass",
                        "",
                    )

                    free_cancellation = rate.get(
                        "freeCancellation",
                        False,
                    )

                    cancellation_policies = (
                        self._parse_cancellation_policies(
                            rate
                        )
                    )

                    result = HotelOption(

                        hotel_code=hotel_code,

                        name=hotel_name,

                        location=destination,

                        category=category,

                        room_code=room_code,

                        room_name=room_name,

                        board=board,

                        price_per_night=(
                            price_per_night
                        ),

                        total_price=(
                            total_price
                        ),

                        currency=currency,

                        check_in_date=(
                            check_in_date.isoformat()
                        ),

                        check_out_date=(
                            check_out_date.isoformat()
                        ),

                        rate_key=rate_key,

                        rate_type=rate_type,

                        rate_class=rate_class,

                        free_cancellation=(
                            free_cancellation
                        ),

                        cancellation_policies=(
                            cancellation_policies
                        ),

                        provider="hotelbeds",
                    )

                    results.append(
                        result
                    )

        return results

    @staticmethod
    def _get_price(
        rate: dict,
    ) -> float:

        # Prefer sellingRate if available.

        if rate.get(
            "sellingRate"
        ) is not None:

            return float(
                rate["sellingRate"]
            )

        # Otherwise use net.

        if rate.get(
            "net"
        ) is not None:

            return float(
                rate["net"]
            )

        return 0.0

    @staticmethod
    def _get_rate_currency(
        rate: dict,
    ) -> str:

        # Use rate-level currency only
        # if Hotelbeds provides it.

        if rate.get(
            "currency"
        ):

            return rate[
                "currency"
            ]

        return ""

    @staticmethod
    def _parse_cancellation_policies(
        rate: dict,
    ) -> list[CancellationPolicy]:

        policies = []

        for policy in rate.get(
            "cancellationPolicies",
            [],
        ):

            policies.append(
                CancellationPolicy(

                    amount=float(
                        policy.get(
                            "amount",
                            0,
                        )
                    ),

                    from_date=policy.get(
                        "from",
                        "",
                    ),
                )
            )

        return policies