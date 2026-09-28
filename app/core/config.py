import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "AI Data Analyst / SQL Agent"
APP_VERSION = "1.0.0"


# ============================================================
# VALIDATION
# ============================================================

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured. "
        "Please add it to the .env file."
    )