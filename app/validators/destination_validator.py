from app.models.destination import DestinationResearch


INVALID_TRANSPORT = {
    "airplane",
    "aircraft",
    "helicopter",
    "bicycle",
    "private car",
    "rental car",
    "van",
    "limousine",
}


def validate_destination_research(
    research: DestinationResearch,
) -> DestinationResearch:

    # Remove invalid transportation methods
    research.local_transport = [
        item
        for item in research.local_transport
        if item.lower().strip() not in INVALID_TRANSPORT
    ]

    # Remove duplicates
    research.neighborhoods = list(
        dict.fromkeys(research.neighborhoods)
    )

    research.must_see = list(
        dict.fromkeys(research.must_see)
    )

    research.food = list(
        dict.fromkeys(research.food)
    )

    research.local_transport = list(
        dict.fromkeys(research.local_transport)
    )

    return research