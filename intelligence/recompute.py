import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import DATABASE_URL_2026, FORM_WINDOW
from elo import (
    get_k_factor, get_goal_multiplier,
    get_actual_score, compute_expected_score,
    compute_new_rating
)

engine = create_engine(DATABASE_URL_2026)

def compute_form(session, team_id: int) -> str:
    results = session.execute(text("""
        SELECT home_team_id, away_team_id, home_goals, away_goals
        FROM matches
        WHERE status = 'FINISHED'
        AND home_goals IS NOT NULL
        AND away_goals IS NOT NULL
        AND (home_team_id = :team_id OR away_team_id = :team_id)
        ORDER BY date DESC
        LIMIT :window
    """), {"team_id": team_id, "window": FORM_WINDOW}).fetchall()

    form = []
    for row in results:
        home_id, away_id, home_goals, away_goals = row
        if home_id == team_id:
            if home_goals > away_goals:
                form.append("W")
            elif home_goals < away_goals:
                form.append("L")
            else:
                form.append("D")
        else:
            if away_goals > home_goals:
                form.append("W")
            elif away_goals < home_goals:
                form.append("L")
            else:
                form.append("D")

    # Results come back newest first, reverse for chronological order
    return "".join(reversed(form))


def update_standings(session, team_id: int):
    stats = session.execute(text("""
    SELECT
        COUNT(*) as played,
        COALESCE(SUM(CASE
            WHEN (home_team_id = :tid AND home_goals > away_goals)
            OR (away_team_id = :tid AND away_goals > home_goals)
            THEN 1 ELSE 0 END), 0) as won,
        COALESCE(SUM(CASE
            WHEN home_goals = away_goals THEN 1 ELSE 0 END), 0) as drawn,
        COALESCE(SUM(CASE
            WHEN (home_team_id = :tid AND home_goals < away_goals)
            OR (away_team_id = :tid AND away_goals < home_goals)
            THEN 1 ELSE 0 END), 0) as lost,
        COALESCE(SUM(CASE WHEN home_team_id = :tid THEN home_goals
                 ELSE away_goals END), 0) as goals_for,
        COALESCE(SUM(CASE WHEN home_team_id = :tid THEN away_goals
                 ELSE home_goals END), 0) as goals_against
    FROM matches
    WHERE status = 'FINISHED'
    AND home_goals IS NOT NULL
    AND away_goals IS NOT NULL
    AND (home_team_id = :tid OR away_team_id = :tid)
"""), {"tid": team_id}).fetchone()

    played, won, drawn, lost, goals_for, goals_against = stats
    points = (won * 3) + drawn
    goals_diff = goals_for - goals_against
    form = compute_form(session, team_id)

    session.execute(text("""
        UPDATE group_standings
        SET played = :played,
            won = :won,
            drawn = :drawn,
            lost = :lost,
            points = :points,
            goals_for = :goals_for,
            goals_against = :goals_against,
            goals_diff = :goals_diff,
            form = :form
        WHERE team_id = :team_id
    """), {
        "played": played, "won": won, "drawn": drawn,
        "lost": lost, "points": points, "goals_for": goals_for,
        "goals_against": goals_against, "goals_diff": goals_diff,
        "form": form, "team_id": team_id
    })


def recompute_elo(session):
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

    ratings = {}

    def get_rating(team_id):
        if team_id not in ratings:
            ratings[team_id] = 1000.0
        return ratings[team_id]

    # Clear existing elo ratings and recompute fresh
    session.execute(text("DELETE FROM elo_ratings"))

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

        from data.models_2026 import EloRating
        session.add(EloRating(
            team_id=home_id, match_id=match_id, stage=stage,
            rating_before=home_rating, rating_after=new_home,
        ))
        session.add(EloRating(
            team_id=away_id, match_id=match_id, stage=stage,
            rating_before=away_rating, rating_after=new_away,
        ))

        ratings[home_id] = new_home
        ratings[away_id] = new_away

    return ratings


def run_post_match_recompute():
    with Session(engine) as session:
        # Get all teams that have played
        teams = session.execute(text("""
            SELECT DISTINCT team_id FROM group_standings
        """)).fetchall()

        print(f"Recomputing standings and form for {len(teams)} teams...")
        for (team_id,) in teams:
            update_standings(session, team_id)

        print("Recomputing Elo ratings...")
        final_ratings = recompute_elo(session)

        session.commit()
        print("Post-match recompute complete.")

        # Sanity check — top 10
        print("\nCurrent Elo Rankings:")
        sorted_ratings = sorted(final_ratings.items(), key=lambda x: x[1], reverse=True)
        for rank, (team_id, rating) in enumerate(sorted_ratings[:10], 1):
            team = session.execute(
                text("SELECT name FROM teams WHERE id = :id"),
                {"id": team_id}
            ).fetchone()
            print(f"{rank}. {team[0]}: {rating:.1f}")


if __name__ == "__main__":
    run_post_match_recompute()