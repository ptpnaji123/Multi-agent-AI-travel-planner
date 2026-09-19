from app.llm.mistral import llm
from app.models.destination import DestinationResearch
from app.tools.web_search import search_web
from app.rag.vectorstore import get_vectorstore
from app.validators.destination_validator import (
    validate_destination_research
)

def destination_agent(destination: str) -> DestinationResearch:

    # --------------------------------------------------
    # 1. WEB SEARCH
    # --------------------------------------------------

    queries = {
        "attractions": f"{destination} top attractions 2026",
        "transport": f"{destination} public transport 2026",
        "travel": f"{destination} visa safety best time to visit 2026",
    }

    web_sections = []

    for category, query in queries.items():

        results = search_web(
            query,
            max_results=2
        )

        web_sections.append(
            f"\n### WEB {category.upper()}\n"
        )

        for result in results:

            content = result.get(
                "content",
                ""
            )[:1200]

            web_sections.append(
                f"""
Title: {result.get("title", "")}
URL: {result.get("url", "")}

Content:
{content}

-------------------------
"""
            )

    web_research = "\n".join(web_sections)

    # --------------------------------------------------
    # 2. LOCAL RAG SEARCH
    # --------------------------------------------------

    vectorstore = get_vectorstore()

    rag_results = vectorstore.similarity_search(
        f"{destination} attractions transportation food neighborhoods visa safety",
        k=5
    )

    rag_sections = []

    for result in rag_results:

        rag_sections.append(
            f"""
Source: {result.metadata.get("source", "")}

Content:
{result.page_content}

-------------------------
"""
        )

    rag_research = "\n".join(rag_sections)

    # --------------------------------------------------
    # 3. MISTRAL STRUCTURED EXTRACTION
    # --------------------------------------------------

    structured_llm = llm.with_structured_output(
        DestinationResearch
    )

    prompt = f"""
You are a travel research extraction agent.

Destination: {destination}

You have TWO information sources:

SOURCE 1: CURRENT WEB RESEARCH
SOURCE 2: LOCAL TRAVEL KNOWLEDGE BASE

Use both sources.

IMPORTANT RULES:
1. Prefer current web information when available.
2. Use local RAG information to supplement the web research.
3. Only include information supported by the provided sources.
4. Do NOT mix categories.
5. Remove duplicates.
6. Return clean names without brackets or unnecessary formatting.
7. Do NOT use your own knowledge.
8. Do NOT invent information.
9. Do NOT repeat information.
10. Keep each item in the correct category.

Rules for each field:

best_season:
Return ONE short sentence.

neighborhoods:
Return 3-5 actual neighborhood/area names.
If unavailable, return [].

must_see:
Return 3-5 actual attractions.
If unavailable, return [].

food:
Return 3-5 actual local foods or dishes.
Do NOT return restaurant names.

visa_notes:
Return only specific visa-related information.
If unavailable, return [].

safety_notes:
Return only specific safety information.
If unavailable, return [].

local_transport:
Return ONLY major public/local transportation methods.
Examples: metro, bus, tram, taxi, ferry.
Maximum 6 transportation methods.
Do NOT include airplanes, helicopters, bicycles,
cars, vans, limousines, etc.

CURRENT WEB RESEARCH:

{web_research}


LOCAL RAG RESEARCH:

{rag_research}
"""

    result = structured_llm.invoke(prompt)

    result = validate_destination_research(result)

    return result