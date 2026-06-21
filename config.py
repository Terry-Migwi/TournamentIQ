from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root
# env_path = Path(__file__).resolve().parent / ".env"
load_dotenv()

API_FOOTBALL_KEY=os.environ.get("API_FOOTBALL_KEY")
API_BASE_URL = "https://v3.football.api-sports.io"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///worldcup.db")
SEASON = int(os.environ.get("SEASON", 2022))
FOOTBALL_DATA_KEY = os.environ["FOOTBALL_DATA_KEY"]
FOOTBALL_DATA_URL = os.environ.get("FOOTBALL_DATA_URL", "https://api.football-data.org/v4")
DATABASE_URL_2026 = os.environ.get("DATABASE_URL_2026", "sqlite:///worldcup_2026.db")
SEASON_2026 = int(os.environ.get("SEASON_2026", 2026))
FORM_WINDOW = int(os.environ.get("FORM_WINDOW", 5))