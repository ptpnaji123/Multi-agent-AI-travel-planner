# ✈️ AI Travel Planner — Multi-Agent Travel Planning System

An Agentic AI travel planning system that researches destinations, searches real flights and hotels, estimates trip costs, generates a day-by-day itinerary, and validates the resulting travel plan.

The project uses **LangGraph for agent orchestration**, **Mistral running locally through Ollama**, **Tavily for web research**, **ChromaDB for RAG**, **Duffel for live flight data**, and **Hotelbeds for hotel availability and pricing**.

---

## 🚀 Project Overview

Planning a trip usually requires searching across multiple platforms for:

- Flights
- Hotels
- Destination information
- Attractions
- Food
- Transportation
- Costs
- Daily schedules

The goal of this project is to combine these tasks into a single **multi-agent AI workflow**.

Instead of relying on one large LLM prompt, the system divides the planning process into specialized stages.

### High-Level Workflow

```text
                        ┌──────────────────┐
                        │   User Request   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Intake Agent   │
                        │     Mistral      │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Coordinator    │
                        └────────┬─────────┘
                                 │
                                 ▼
                  ┌────────────────────────────┐
                  │   Destination Research    │
                  │                            │
                  │ Tavily + RAG + Mistral     │
                  └─────────────┬──────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
       ┌─────────────────┐             ┌─────────────────┐
       │  Flight Agent   │             │   Hotel Agent   │
       │     Duffel      │             │   Hotelbeds     │
       └────────┬────────┘             └────────┬────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Budget Agent   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Itinerary Agent │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Validation    │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Critic / Repair │
                       └─────────────────┘

```
🛠️ TECH STACK
Python
LangGraph
LangChain
Ollama / Mistral
ChromaDB
RAG
Tavily
Duffel API
Hotelbeds API
Pydantic
Streamlit


📁 PROJECT STRUCTURE
travel-planner-agent/
├── app/
│   ├── agents/
│   ├── graph/
│   ├── llm/
│   ├── models/
│   ├── providers/
│   ├── rag/
│   ├── services/
│   ├── tools/
│   └── validators/
├── data/
├── frontend/
│   └── streamlit_app.py
├── tests/
├── .env
├── requirements.txt
└── run.py


🚀 SETUP

1. Clone the repository
git clone <(https://github.com/ptpnaji123/Multi-agent-AI-travel-planner)>
cd travel-planner-agent

2. Create a virtual environment

Windows PowerShell:
python -m venv .venv

Activate it:
.\.venv\Scripts\Activate.ps1

3. Install dependencies
pip install -r requirements.txt

4. Install and start Ollama
Install Ollama and make sure it is running.

Pull the required models:

ollama pull mistral:latest
ollama pull nomic-embed-text

Check:
ollama list

5. Configure environment variables

Create a .env file in the project root:

TAVILY_API_KEY=your_tavily_key
DUFFEL_ACCESS_TOKEN=your_duffel_token
OPENROUTESERVICE_API_KEY=your_openrouteservice_key
HOTELBEDS_API_KEY=your_hotelbeds_key
HOTELBEDS_SECRET=your_hotelbeds_secret

Never commit .env or expose your API keys.

📚 RAG Setup

If the RAG documents have not been indexed yet:
python scripts/ingest_rag.py

▶️ Run the Application
Streamlit UI
From the project root:

streamlit run frontend/streamlit_app.py

Then open:

http://localhost:8501
Command-line version
python run.py

🧪 Example Request
I want to travel from Kochi to Dubai
from December 10 to December 15, 2026.
There is 1 traveler.

The application can then generate:

Kochi → Dubai

✈️ Flight
🏨 Hotel
💰 Estimated Budget
📅 Day-by-Day Itinerary
🌍 Destination Highlights


⚠️ Notes
Flight and hotel prices depend on live provider availability.
Budget values for food, transport, and activities are planning estimates.
API credentials are required for external services.
Mistral runs locally through Ollama.


🔮 Future Improvements
Opening-hours validation
Distance and route optimization
Better activity pricing
Human approval workflow
Itinerary repair and regeneration
PDF / Markdown / calendar export
More travel providers
Automated testing
