import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import API_FOOTBALL_KEY, API_BASE_URL, SEASON, DATABASE_URL
from data.models_2022 import Match

headers = {"x-apisports-key": API_FOOTBALL_KEY}

print("Fetching fixtures from API...")
response = requests.get(
    f"{API_BASE_URL}/fixtures",
    headers=headers,
    params={"league": 1, "season": SEASON}
)
print(f"Got response: {response.status_code}")

data = response.json()["response"]
print(f"Total fixtures fetched: {len(data)}")

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    for entry in data:
        match = Match(
            id=entry["fixture"]["id"],
            home_team_id=entry["teams"]["home"]["id"],
            away_team_id=entry["teams"]["away"]["id"],
            date=entry["fixture"]["date"],
            round=entry["league"]["round"],
            venue_name=entry["fixture"]["venue"]["name"],
            venue_city=entry["fixture"]["venue"]["city"],
            status=entry["fixture"]["status"]["long"],
            home_goals=entry["goals"]["home"],
            away_goals=entry["goals"]["away"],
            home_goals_ht=entry["score"]["halftime"]["home"],
            away_goals_ht=entry["score"]["halftime"]["away"],
            penalty_home=entry["score"]["penalty"]["home"],
            penalty_away=entry["score"]["penalty"]["away"],
        )
        #session.add(match)
        session.merge(match) # for when running the scheduler
    session.commit()
    print("Done! All matches saved to database.")