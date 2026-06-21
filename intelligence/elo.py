# predict expected outcome 

K_FACTORS = {
    # 2026 stage names (football-data.org)
    "GROUP_STAGE": 32,
    "LAST_32": 40,
    "ROUND_OF_16": 50,
    "QUARTER_FINALS": 50,
    "SEMI_FINALS": 60,
    "THIRD_PLACE": 60,
    "FINAL": 60,
    # 2022 stage names (api-football)
    "Group Stage - 1": 32,
    "Group Stage - 2": 32,
    "Group Stage - 3": 32,
    "Round of 16": 50,
    "Quarter-finals": 50,
    "Semi-finals": 60,
    "3rd Place Final": 60,
    "Final": 60,
}

def get_k_factor(stage: str) -> int:
    return K_FACTORS.get(stage, 32)

def get_goal_multiplier(home_goals: int, away_goals: int, went_to_penalties: bool) -> float:
    if went_to_penalties:
        return 1.0
    goal_diff = abs(home_goals - away_goals)
    if goal_diff == 0 or goal_diff == 1:
        return 1.0
    elif goal_diff == 2:
        return 1.5
    else:
        return 1.75

def get_actual_score(home_goals: int, away_goals: int, duration: str, 
                     penalty_home: int = None, penalty_away: int = None):
    if duration == "PENALTY_SHOOTOUT":
        if penalty_home is not None and penalty_away is not None:
            if penalty_home > penalty_away:
                return (0.75, 0.5)
            else:
                return (0.5, 0.75)
        # fallback if penalty scores missing
        if home_goals > away_goals:
            return (0.75, 0.5)
        else:
            return (0.5, 0.75)
    elif home_goals > away_goals:
        return (1.0, 0.0)
    elif away_goals > home_goals:
        return (0.0, 1.0)
    else:
        return (0.5, 0.5)

def compute_expected_score(rating_a: float, rating_b: float) -> float:
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def compute_new_rating(old_rating: float, k: int, g: float, actual: float, expected: float) -> float:
    return old_rating + k * g * (actual - expected)