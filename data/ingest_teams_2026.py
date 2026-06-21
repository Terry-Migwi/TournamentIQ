import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import FOOTBALL_DATA_KEY, FOOTBALL_DATA_URL, SEASON_2026, DATABASE_URL_2026
from data.models_2026 import Team

headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}
response = requests.get(
    f"{FOOTBALL_DATA_URL}/competitions/WC/teams",
    headers=headers,
    params={"season": SEASON_2026}
)
data = response.json()["teams"]

engine = create_engine(DATABASE_URL_2026)

with Session(engine) as session:
    for entry in data:                    # loop over all 32 teams

        team = Team(                      # create one Team object (fill out the form)
            id=entry["id"],
            name=entry["name"],
            tla=entry["tla"],
            founded=entry["founded"],
            crest=entry["crest"],
            venue=entry["venue"],
        )

        #session.add(team)                 # stage this team for saving
        session.merge(team)               # for the scheduler
    session.commit()                      # write ALL 32 teams to the DB at once
    