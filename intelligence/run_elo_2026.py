# ONE-TIME / MANUAL USE ONLY.
# This script has no DELETE guard, running it more than once duplicates
# every row in elo_ratings. For routine recomputes, use recompute.py,
# which clears elo_ratings before rebuilding. Use this script only for
# a fresh backtest run or a one-off check, and clear elo_ratings first
# if you're not sure it's already empty.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import DATABASE_URL_2026
from data.models_2026 import EloRating
from elo import (
    get_k_factor,
    get_goal_multiplier,
    get_actual_score,
    compute_expected_score,
    compute_new_rating,
)

STARTING_RATING = 1000.0

engine = create_engine(DATABASE_URL_2026)

with Session(engine) as session:
    # 1. Load all finished matches in chronological order
    matches = session.execute(text("""
        SELECT id, home_team_id, away_team_id, stage,
            home_goals, away_goals, duration
        FROM matches
        WHERE status = 'FINISHED'
        AND home_team_id IS NOT NULL
        AND away_team_id IS NOT NULL
        AND home_goals IS NOT NULL
        AND away_goals IS NOT NULL
        ORDER BY date ASC
    """)).fetchall()

    print(f"Processing {len(matches)} finished matches...")

    # 2. Track current ratings in memory
    ratings = {}  # team_id → current rating

    def get_rating(team_id):
        if team_id not in ratings:
            ratings[team_id] = STARTING_RATING
        return ratings[team_id]

    # 3. Process each match
    for match in matches:
        match_id, home_id, away_id, stage, home_goals, away_goals, duration = match

        home_rating = get_rating(home_id)
        away_rating = get_rating(away_id)

        k = get_k_factor(stage)
        g = get_goal_multiplier(home_goals, away_goals, duration == "PENALTY_SHOOTOUT")
        home_w, away_w = get_actual_score(home_goals, away_goals, duration)
        home_expected = compute_expected_score(home_rating, away_rating)
        away_expected = compute_expected_score(away_rating, home_rating)

        new_home = compute_new_rating(home_rating, k, g, home_w, home_expected)
        new_away = compute_new_rating(away_rating, k, g, away_w, away_expected)

        # 4. Store rating history for both teams
        session.add(EloRating(
            team_id=home_id,
            match_id=match_id,
            stage=stage,
            rating_before=home_rating,
            rating_after=new_home,
        ))
        session.add(EloRating(
            team_id=away_id,
            match_id=match_id,
            stage=stage,
            rating_before=away_rating,
            rating_after=new_away,
        ))

        # 5. Update in-memory ratings
        ratings[home_id] = new_home
        ratings[away_id] = new_away

    session.commit()
    print("Elo ratings computed and stored.")

    # 6. Print final rankings as sanity check
    print("\nFinal Elo Rankings:")
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    for rank, (team_id, rating) in enumerate(sorted_ratings[:10], 1):
        team = session.execute(
            text("SELECT name FROM teams WHERE id = :id"),
            {"id": team_id}
        ).fetchone()
        print(f"{rank}. {team[0]}: {rating:.1f}")