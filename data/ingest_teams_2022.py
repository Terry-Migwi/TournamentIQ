import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import API_FOOTBALL_KEY, API_BASE_URL, SEASON, DATABASE_URL
from data.models_2022 import Team

headers = {"x-apisports-key": API_FOOTBALL_KEY}
response = requests.get(
    f"{API_BASE_URL}/teams",
    headers=headers,
    params={"league": 1, "season": SEASON}
)
data = response.json()["response"]

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    for entry in data:                    # loop over all 32 teams
        team_data = entry["team"]         # grab the team sub-dict
        venue_data = entry["venue"]       # grab the venue sub-dict

        team = Team(                      # create one Team object (fill out the form)
            id=team_data["id"],
            name=team_data["name"],
            code=team_data["code"],
            country=team_data["country"],
            founded=team_data["founded"],
            national=team_data["national"],
            logo=team_data["logo"],
            venue_name=venue_data["name"],
            venue_city=venue_data["city"],
            venue_capacity=venue_data["capacity"],
        )

        #session.add(team)                 # stage this team for saving
        session.merge(team) # for when running the scheduler
    session.commit()                      # write ALL 32 teams to the DB at once