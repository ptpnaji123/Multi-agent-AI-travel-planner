from app.llm.mistral import llm

from app.models.trip_request import TripRequest
from app.models.destination import DestinationResearch

from app.tools.web_search import search_web
from app.rag.vectorstore import get_vectorstore

from app.validators.destination_validator import (
    validate_destination_research,
)


# ============================================================
# WEB SECTION EXTRACTION
# ============================================================

def get_web_section(
    web_research: str,
    section_name: str,
) -> str:
    """
    Extract one category section from the combined
    Tavily research.

    Example:
        ### WEB ATTRACTIONS
        ...
        ### WEB FOOD
        ...

    This function returns only the requested section.
    """

    start_marker = (
        f"### WEB {section_name.upper()}"
    )

    start = web_research.find(
        start_marker
    )

    if start == -1:
        return ""

    start += len(start_marker)

    remaining = web_research[start:]

    next_section = remaining.find(
        "### WEB "
    )

    if next_section == -1:
        return remaining.strip()

    return remaining[
        :next_section
    ].strip()


# ============================================================
# LLM LIST EXTRACTION
# ============================================================

def extract_list(
    category: str,
    destination: str,
    research_text: str,
) -> list[str]:
    """
    Ask Mistral to extract one category from research.

    The model is instructed to return one item per line
    instead of JSON/Pydantic/list syntax because this is
    more reliable with the local Mistral model.
    """

    if not research_text.strip():
        print(
            f"\nNo research available for {category}."
        )
        return []

    prompt = f"""
You are a strict information extraction system.

Destination:
{destination}

CATEGORY TO EXTRACT:
{category}

Your ONLY task is to extract items belonging to
the requested category.

STRICT RULES:

1. Use ONLY information explicitly present in the
   supplied research.

2. Do NOT use your own knowledge.

3. Do NOT invent information.

4. Do NOT summarize the research.

5. Do NOT explain the answer.

6. Do NOT repeat the research.

7. Do NOT include headings.

8. Do NOT include numbering.

9. Do NOT include bullet symbols.

10. Return ONE item per line.

11. Return a maximum of 8 items.

12. If there is no valid information, return:
EMPTY

IMPORTANT:
Only return items belonging to the requested category.

For example, if the category is:
TRADITIONAL LOCAL FOOD / DISHES

A valid answer is:

Machboos
Al Harees
Shawarma

Do NOT return:
Dubai Marina
Burj Khalifa
Dubai Metro

because those are not food items.

RESEARCH:
{research_text}

FINAL ANSWER:
Return ONLY the extracted items.
"""

    print(
        f"\nExtracting {category}..."
    )

    response = llm.invoke(
        prompt
    )

    text = response.content.strip()

    print(
        f"\nRaw {category} response:"
    )
    print(text)

    return parse_line_response(
        text
    )


# ============================================================
# RESPONSE PARSER
# ============================================================

def parse_line_response(
    text: str,
) -> list[str]:
    """
    Convert Mistral's line-based response into
    a clean Python list.

    Handles:
        Item
        - Item
        * Item
        1. Item
        2) Item
    """

    text = text.strip()

    if not text:
        return []

    if text.upper() == "EMPTY":
        return []

    items = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove markdown code fences
        if line.startswith("```"):
            continue

        # Remove bullet
        if line.startswith("-"):
            line = line[1:].strip()

        elif line.startswith("*"):
            line = line[1:].strip()

        # Remove numbered format:
        # 1. Item
        # 2) Item
        if (
            len(line) >= 3
            and line[0].isdigit()
            and line[1] in [".", ")"]
        ):
            line = line[2:].strip()

        if not line:
            continue

        lower = line.lower()

        # Ignore explanatory text
        ignored_prefixes = (
            "here are",
            "here is",
            "the following",
            "based on",
            "according to",
            "it seems",
            "i found",
            "the research",
            "summary",
            "final answer",
            "answer:",
            "research:",
            "items:",
        )

        if lower.startswith(
            ignored_prefixes
        ):
            continue

        # Ignore category headings
        if lower.endswith(":"):
            continue

        items.append(line)

    # Remove duplicates while preserving order
    cleaned_items = []

    seen = set()

    for item in items:

        normalized = item.lower().strip()

        if normalized in seen:
            continue

        seen.add(normalized)

        cleaned_items.append(
            item
        )

    return cleaned_items[:8]


# ============================================================
# DESTINATION AGENT
# ============================================================

def destination_agent(
    trip_request: TripRequest,
) -> DestinationResearch:
    """
    Research and structure destination information.

    Sources:
        1. Tavily web research
        2. Local RAG travel guides

    The LLM is used for category extraction.
    Python handles cleaning and validation.
    """

    destination = (
        trip_request.destination
    )

    print(
        f"\nResearching destination: "
        f"{destination}"
    )

    # ========================================================
    # 1. WEB SEARCH
    # ========================================================

    queries = {

        "attractions": (
            f"{destination} top tourist attractions "
            f"2026"
        ),

        "neighborhoods": (
            f"{destination} best neighborhoods "
            f"areas to visit tourists 2026"
        ),

        "food": (
            f"{destination} traditional local food "
            f"dishes 2026"
        ),

        "transport": (
            f"{destination} public transportation "
            f"metro bus tram ferry taxi 2026"
        ),

        "travel_info": (
            f"{destination} visa requirements "
            f"safety travel tips best time to visit 2026"
        ),
    }

    web_sections = []

    for category, query in queries.items():

        print(
            f"\nSearching web: "
            f"{category}"
        )

        results = search_web(
            query,
            max_results=3,
        )

        web_sections.append(
            f"\n### WEB {category.upper()}\n"
        )

        for result in results:

            title = result.get(
                "title",
                "",
            )

            url = result.get(
                "url",
                "",
            )

            content = result.get(
                "content",
                "",
            )

            # Keep the amount of text sent to
            # the model manageable.
            content = content[:1800]

            web_sections.append(
                f"""
Title:
{title}

URL:
{url}

Content:
{content}

-------------------------
"""
            )

    web_research = "\n".join(
        web_sections
    )

    # ========================================================
    # 2. EXTRACT WEB SECTIONS
    # ========================================================

    attractions_web = get_web_section(
        web_research,
        "attractions",
    )

    neighborhoods_web = get_web_section(
        web_research,
        "neighborhoods",
    )

    food_web = get_web_section(
        web_research,
        "food",
    )

    transport_web = get_web_section(
        web_research,
        "transport",
    )

    travel_info_web = get_web_section(
        web_research,
        "travel_info",
    )

    # ========================================================
    # 3. LOCAL RAG SEARCH
    # ========================================================

    print(
        "\nSearching local RAG..."
    )

    vectorstore = get_vectorstore()

    rag_results = vectorstore.similarity_search(
        (
            f"{destination} "
            f"attractions neighborhoods "
            f"food transportation visa safety"
        ),
        k=8,
    )

    rag_sections = []

    for result in rag_results:

        source = result.metadata.get(
            "source",
            "",
        )

        content = result.page_content

        rag_sections.append(
            f"""
Source:
{source}

Content:
{content}

-------------------------
"""
        )

    rag_research = "\n".join(
        rag_sections
    )

    # ========================================================
    # 4. DEBUG INFORMATION
    # ========================================================

    print(
        "\n========== WEB SECTION SUMMARY =========="
    )

    print(
        f"Attractions web chars: "
        f"{len(attractions_web)}"
    )

    print(
        f"Neighborhoods web chars: "
        f"{len(neighborhoods_web)}"
    )

    print(
        f"Food web chars: "
        f"{len(food_web)}"
    )

    print(
        f"Transport web chars: "
        f"{len(transport_web)}"
    )

    print(
        f"Travel info web chars: "
        f"{len(travel_info_web)}"
    )

    print(
        f"\nRAG chars: "
        f"{len(rag_research)}"
    )

    print(
        "========== END WEB SECTION SUMMARY ==========\n"
    )

    # ========================================================
    # 5. CATEGORY-SPECIFIC RESEARCH
    # ========================================================

    # We deliberately provide each extractor with
    # the most relevant web section.
    #
    # The RAG is included as supplementary information.

    neighborhood_research = f"""
WEB NEIGHBORHOOD RESEARCH:

{neighborhoods_web}

LOCAL RAG RESEARCH:

{rag_research}
"""

    attraction_research = f"""
WEB ATTRACTION RESEARCH:

{attractions_web}

LOCAL RAG RESEARCH:

{rag_research}
"""

    food_research = f"""
WEB FOOD RESEARCH:

{food_web}

LOCAL RAG RESEARCH:

{rag_research}
"""

    transport_research = f"""
WEB TRANSPORT RESEARCH:

{transport_web}

LOCAL RAG RESEARCH:

{rag_research}
"""

    # ========================================================
    # 6. EXTRACT NEIGHBORHOODS
    # ========================================================

    neighborhoods = extract_list(
        category=(
            "NEIGHBORHOODS / DISTRICTS / "
            "TOURIST AREAS"
        ),
        destination=destination,
        research_text=neighborhood_research,
    )

    # ========================================================
    # 7. EXTRACT ATTRACTIONS
    # ========================================================

    must_see = extract_list(
        category=(
            "TOURIST ATTRACTIONS / "
            "PLACES TO VISIT"
        ),
        destination=destination,
        research_text=attraction_research,
    )

    # ========================================================
    # 8. EXTRACT FOOD
    # ========================================================

    food = extract_list(
        category=(
            "TRADITIONAL LOCAL FOOD / "
            "DISHES"
        ),
        destination=destination,
        research_text=food_research,
    )

    # ========================================================
    # 9. EXTRACT TRANSPORT
    # ========================================================

    local_transport = extract_list(
        category=(
            "PUBLIC / LOCAL "
            "TRANSPORTATION METHODS"
        ),
        destination=destination,
        research_text=transport_research,
    )

    # ========================================================
    # 10. VALIDATE TRANSPORT
    # ========================================================

    # The validator removes things such as:
    # airplanes, bicycles, private cars, etc.

    research = DestinationResearch(
        destination=destination,

        # We currently leave these empty because
        # best-season / visa / safety extraction
        # will be handled separately.
        best_season="",

        neighborhoods=neighborhoods,

        must_see=must_see,

        food=food,

        visa_notes=[],

        safety_notes=[],

        local_transport=local_transport,
    )

    research = validate_destination_research(
        research
    )

    # ========================================================
    # 11. FINAL RESULT
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "DESTINATION RESEARCH RESULT"
    )

    print(
        "=============================="
    )

    print(
        f"Destination: "
        f"{research.destination}"
    )

    print(
        f"Neighborhoods: "
        f"{research.neighborhoods}"
    )

    print(
        f"Must see: "
        f"{research.must_see}"
    )

    print(
        f"Food: "
        f"{research.food}"
    )

    print(
        f"Transport: "
        f"{research.local_transport}"
    )

    print(
        f"Visa: "
        f"{research.visa_notes}"
    )

    print(
        f"Safety: "
        f"{research.safety_notes}"
    )

    print(
        f"Best season: "
        f"{research.best_season}"
    )

    return research