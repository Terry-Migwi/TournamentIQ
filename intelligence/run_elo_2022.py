import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import DATABASE_URL
from elo import (
    get_k_factor, get_goal_multiplier,
    get_actual_score, compute_expected_score,
    compute_new_rating
)

STARTING_RATING = 1000.0
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    matches = session.execute(text("""
        SELECT id, home_team_id, away_team_id, round,
               home_goals, away_goals, penalty_home, penalty_away
        FROM matches
        WHERE status = 'Match Finished'
        AND home_team_id IS NOT NULL
        AND away_team_id IS NOT NULL
        ORDER BY date ASC
    """)).fetchall()

    print(f"Processing {len(matches)} finished matches...")

    ratings = {}

    def get_rating(team_id):
        if team_id not in ratings:
            ratings[team_id] = STARTING_RATING
        return ratings[team_id]

    for match in matches:
        match_id, home_id, away_id, round_name, home_goals, away_goals, penalty_home, penalty_away = match

        went_to_penalties = penalty_home is not None and penalty_away is not None
        duration = "PENALTY_SHOOTOUT" if went_to_penalties else "REGULAR"

        home_rating = get_rating(home_id)
        away_rating = get_rating(away_id)

        k = get_k_factor(round_name)
        g = get_goal_multiplier(home_goals, away_goals, went_to_penalties)
        home_w, away_w = get_actual_score(home_goals, away_goals, duration)
        home_expected = compute_expected_score(home_rating, away_rating)
        away_expected = compute_expected_score(away_rating, home_rating)

        new_home = compute_new_rating(home_rating, k, g, home_w, home_expected)
        new_away = compute_new_rating(away_rating, k, g, away_w, away_expected)

        ratings[home_id] = new_home
        ratings[away_id] = new_away

    print("\n2022 World Cup Final Elo Rankings:")
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    for rank, (team_id, rating) in enumerate(sorted_ratings[:10], 1):
        team = session.execute(
            text("SELECT name FROM teams WHERE id = :id"),
            {"id": team_id}
        ).fetchone()
        print(f"{rank}. {team[0]}: {rating:.1f}")