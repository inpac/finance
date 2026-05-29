import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "finance.db"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_CURRENCY = "USD"

SAFE_WITHDRAWAL_RATE = 0.04
DEFAULT_MARKET_RETURN = 0.07
HIGH_INTEREST_THRESHOLD = 0.10

DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
