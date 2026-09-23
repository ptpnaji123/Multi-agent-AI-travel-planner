import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# TAVILY
# ============================================================

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)


# ============================================================
# DUFFEL
# ============================================================

DUFFEL_ACCESS_TOKEN = os.getenv(
    "DUFFEL_ACCESS_TOKEN"
)


# ============================================================
# OPENROUTESERVICE
# ============================================================

OPENROUTESERVICE_API_KEY = os.getenv(
    "OPENROUTESERVICE_API_KEY"
)


# ============================================================
# HOTELBEDS
# ============================================================

HOTELBEDS_API_KEY = os.getenv(
    "HOTELBEDS_API_KEY"
)

HOTELBEDS_SECRET = os.getenv(
    "HOTELBEDS_SECRET"
)