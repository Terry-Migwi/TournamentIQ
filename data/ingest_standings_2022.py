import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import API_FOOTBALL_KEY, API_BASE_URL, SEASON, DATABASE_URL
from data.models_2022 import GroupStandings

headers = {"x-apisports-key": API_FOOTBALL_KEY}

print("Fetching standings from API...")
response = requests.get(
    f"{API_BASE_URL}/standings",
    headers=headers,
    params={"league": 1, "season": SEASON}
)
print(f"Got response: {response.status_code}")

data = response.json()["response"]
groups = data[0]["league"]["standings"]

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    for group in groups:
        for standing in group:
            gs = GroupStandings(
                team_id=standing["team"]["id"],
                group_name=standing["group"],
                rank=standing["rank"],
                points=standing["points"],
                goals_diff=standing["goalsDiff"],
                played=standing["all"]["played"],
                won=standing["all"]["win"],
                drawn=standing["all"]["draw"],
                lost=standing["all"]["lose"],
                goals_for=standing["all"]["goals"]["for"],
                goals_against=standing["all"]["goals"]["against"],
            )
            #session.add(gs)
            session.merge(gs) # for when running the scheduler
    session.commit()
    print("Done! All standings saved to database.")