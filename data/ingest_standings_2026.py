import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import FOOTBALL_DATA_KEY, FOOTBALL_DATA_URL, SEASON_2026, DATABASE_URL_2026
from data.models_2026 import GroupStandings

headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}

print("Fetching matches to derive group names...")
matches_response = requests.get(
    f"{FOOTBALL_DATA_URL}/competitions/WC/matches",
    headers=headers,
    params={"season": SEASON_2026}
)
matches_data = matches_response.json()["matches"]

# Build team_id → group mapping from group stage matches
team_group = {}
for match in matches_data:
    if match["stage"] == "GROUP_STAGE":
        group = match["group"]
        if match["homeTeam"]["id"]:
            team_group[match["homeTeam"]["id"]] = group
        if match["awayTeam"]["id"]:
            team_group[match["awayTeam"]["id"]] = group

print(f"Group mappings built for {len(team_group)} teams")

print("Fetching standings...")
standings_response = requests.get(
    f"{FOOTBALL_DATA_URL}/competitions/WC/standings",
    headers=headers,
    params={"season": SEASON_2026}
)
standings_data = standings_response.json()

# Get only TOTAL standings
total_standings = [
    s for s in standings_data["standings"]
    if s["type"] == "TOTAL"
][0]

engine = create_engine(DATABASE_URL_2026)

with Session(engine) as session:
    for entry in total_standings["table"]:
        team_id = entry["team"]["id"]
        gs = GroupStandings(
            team_id=team_id,
            group_name=team_group.get(team_id, "UNKNOWN"),
            position=0,
            played=entry["playedGames"],
            won=entry["won"],
            drawn=entry["draw"],
            lost=entry["lost"],
            points=entry["points"],
            goals_for=entry["goalsFor"],
            goals_against=entry["goalsAgainst"],
            goals_diff=entry["goalDifference"],
        )
        session.merge(gs)
    session.commit()
    print("Done! All standings saved to database.")

     # recompute position per group, not globally
    for group in session.query(GroupStandings.group_name).distinct():
        group_name = group[0]
        rows = (
            session.query(GroupStandings)
            .filter_by(group_name=group_name)
            .order_by(
                GroupStandings.points.desc(),
                GroupStandings.goals_diff.desc(),
                GroupStandings.goals_for.desc(),
            )
            .all()
        )
        for i, row in enumerate(rows, start=1):
            row.position = i
    session.commit()
    print("Done! Standings saved with per-group position.")