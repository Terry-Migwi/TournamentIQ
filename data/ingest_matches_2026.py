import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import FOOTBALL_DATA_KEY, FOOTBALL_DATA_URL, SEASON_2026, DATABASE_URL_2026
from data.models_2026 import Match

headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}

print("Fetching matches from football-data.org...")
response = requests.get(
    f"{FOOTBALL_DATA_URL}/competitions/WC/matches",
    headers=headers,
    params={"season": SEASON_2026}
)
print(f"Got response: {response.status_code}")

data = response.json()["matches"]
print(f"Total matches fetched: {len(data)}")

engine = create_engine(DATABASE_URL_2026)

skipped = []

with Session(engine) as session:
    for entry in data:
        home_goals = entry["score"]["fullTime"]["home"]
        away_goals = entry["score"]["fullTime"]["away"]

        if entry["status"] == "FINISHED" and (home_goals is None or away_goals is None):
            skipped.append(entry["id"])
            continue

        match = Match(
            id=entry["id"],
            home_team_id=entry["homeTeam"]["id"],
            away_team_id=entry["awayTeam"]["id"],
            season=SEASON_2026,
            stage=entry["stage"],
            matchday=entry["matchday"],
            date=entry["utcDate"],
            status=entry["status"],
            duration=entry["score"]["duration"],
            home_goals=home_goals,
            away_goals=away_goals,
            home_goals_ht=entry["score"]["halfTime"]["home"],
            away_goals_ht=entry["score"]["halfTime"]["away"],
        )
        session.merge(match)
    session.commit()
    print("Done! All matches saved to database.")

if skipped:
    print(f"Skipped {len(skipped)} FINISHED match(es) with missing scores: {skipped}")
    print("These will retry on the next scheduled poll.")