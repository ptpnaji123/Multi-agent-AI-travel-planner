from app.services.currency_service import (
    CurrencyService,
    convert_to_inr,
)


def main():

    service = CurrencyService()

    print("\n==============================")
    print("CURRENCY SERVICE TEST")
    print("==============================")

    # -----------------------------------------
    # EUR -> INR
    # -----------------------------------------

    eur_rate = service.get_exchange_rate(
        from_currency="EUR",
        to_currency="INR",
    )

    print(
        f"\nEUR -> INR rate: "
        f"{eur_rate}"
    )

    eur_amount = service.convert_currency(
        amount=236.11,
        from_currency="EUR",
        to_currency="INR",
    )

    print(
        f"236.11 EUR = "
        f"{eur_amount} INR"
    )

    # -----------------------------------------
    # USD -> INR
    # -----------------------------------------

    usd_rate = service.get_exchange_rate(
        from_currency="USD",
        to_currency="INR",
    )

    print(
        f"\nUSD -> INR rate: "
        f"{usd_rate}"
    )

    usd_amount = service.convert_currency(
        amount=219.47,
        from_currency="USD",
        to_currency="INR",
    )

    print(
        f"219.47 USD = "
        f"{usd_amount} INR"
    )

    # -----------------------------------------
    # INR -> INR
    # -----------------------------------------

    inr_amount = service.convert_currency(
        amount=10000,
        from_currency="INR",
        to_currency="INR",
    )

    print(
        f"\n10000 INR = "
        f"{inr_amount} INR"
    )

    # -----------------------------------------
    # Helper function
    # -----------------------------------------

    hotel_inr = convert_to_inr(
        amount=236.11,
        currency="EUR",
    )

    print(
        f"\nHotel price converted to INR: "
        f"{hotel_inr} INR"
    )


if __name__ == "__main__":
    main()