import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import API_FOOTBALL_KEY, API_BASE_URL, SEASON_2026
import json


#headers = {"x-apisports-key": API_FOOTBALL_KEY}
#status = requests.get(f"{API_BASE_URL}/status", headers=headers)
#print("STATUS:", status.status_code)
#print(status.json())

# 2. Check World Cup (league 1) season coverage
#leagues = requests.get(f"{API_BASE_URL}/leagues", headers=headers, params={"id": 1})
#print("LEAGUES:", leagues.status_code)
#print(leagues.json())

# 3. Check teams
#teams = requests.get(
 #   f"{API_BASE_URL}/teams",
 #   headers=headers,
 #   params={"league": 1, "season": SEASON}
#)
#print(teams.status_code)
#print(teams.json())

# Check standings
#group_standings = requests.get(
#    f"{API_BASE_URL}/standings",
#    headers=headers,
#    params={"league": 1, "season": SEASON}
#)
#print(group_standings.status_code)
#print(group_standings.json())

# Check fixtures
# fixtures = requests.get(
#  f"{API_BASE_URL}/fixtures",
#   headers=headers,
#   params={"league": 1, "season": SEASON}
#)
#print(group_standings.status_code)
#print(fixtures.json())

from config import FOOTBALL_DATA_KEY, FOOTBALL_DATA_URL

headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}

#response = requests.get(
#    f"{FOOTBALL_DATA_URL}/competitions/WC/matches",
#    params={"season": 2026},
#    headers=headers
#)
#print(response.status_code)
#print(response.json())

# Teams
#teams = requests.get(
   # f"{FOOTBALL_DATA_URL}/competitions/WC/teams",
  #  params={"season": 2026},
 #   headers=headers
#)
#print("TEAMS:")
#print(teams.json())
#teams_data = teams.json()
#print(teams_data["teams"][0])  # just the first team

# Standings
#standings = requests.get(
#    f"{FOOTBALL_DATA_URL}/competitions/WC/standings",
#    params={"season": 2026},
#    headers=headers
#)
#print("STANDINGS:")
#print(standings.json())
#standings_data = standings.json()
# first standing group, first team row
#standings_data = standings.json()
#for s in standings_data["standings"][:3]:
   # print(s["stage"], s["type"], s["group"])
#print(standings_data["standings"][0]["table"][0])
#total_standing = [s for s in standings_data["standings"] if s["type"] == "TOTAL"][0]
#print(f"Teams in table: {len(total_standing['table'])}")
#print(total_standing["table"][0])
#print(total_standing["table"][1])


standings_response = requests.get(
    f"{FOOTBALL_DATA_URL}/competitions/WC/standings",
    headers=headers,
    params={"season": SEASON_2026}
)
standings_data = standings_response.json()
print(json.dumps(standings_data["standings"][:2], indent=2))