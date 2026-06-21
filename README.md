# TournamentIQ

## Problem

Most tournament predictions lean on reputation. A team's name, its history, last World Cup's result, all carry weight before the tournament starts. But how do we know which team performed the best in that specific tournament, regardless of their reputation or historical data?

## Solution

TournamentIQ is a live intelligence system that tracks team strength using Elo Ratings. Every team starts at the same baseline rating, with no prior history carried in. Ratings update after every match based on the stage, the goal margin, and the team's probability to win in relation to the competing team.


## Source of Data

Two APIs feed this project, for two different reasons.

`football-data.org` is the primary source, live 2026 match, fixture, and standings data, on a free tier. `api-football.com` was the original choice, but its free tier does not carry 2026 World Cup data, so it was kept instead for 2022 data, used to backtest the rating system before trusting it on live data.


## Use Cases

- **Pre match intelligence.** A current Elo rating for every team, recalculated after each result, usable as a win probability input for a given matchup.
- **Tournament analysis.** Group level metrics, such as how tightly or widely a group's teams are rated after their opening matches, as an early signal for how settled or open a group is likely to be.
- **A foundation for prediction.** Elo currently produces a win probability, not a score. It is designed as an input feature for a planned Poisson based scoring model, rather than a complete prediction system on its own.
- **A domain agnostic pattern.** The ingestion, schema, and rating design are not football specific. The same structure, live event data feeding a continuously recalculated strength score, applies to other competitive or ranked domains.

## Architecture

**Two databases, SQLite.** `worldcup.db` holds 2022 backtest data from api-football.com. `worldcup_2026.db` holds live 2026 data from football-data.org. SQLite was chosen over a server based database like Postgres because this project runs from a single machine with a single writer, removing setup that would not be relevant for this stage.

**SQLAlchemy ORM.** Schema is defined in Python, not raw SQL, across four models, `Team`, `Match`, `GroupStanding`, and `EloRating`. `EloRating` is a separate table rather than folded into `GroupStanding`, so a change to the rating formula stays a schema change in one place, and full rating history stays queryable, not just the current number.

**Elo engine, written as pure functions.** `elo.py` has no database dependency, the same five functions run identically for the 2022 backtest and live 2026 ratings. Ratings update based on match stage, goal margin, and how surprising a result was relative to the two teams' ratings going in.

**Recompute pipeline.** `recompute.py` rebuilds form, standings, and Elo ratings from raw match data after every result, rather than trusting any single externally computed aggregate. Standings are derived independently from the project's own match data, not copied directly from the API's own standings calculation, since that is where one of the data quality issues documented in the full write up originated.

**Scheduled ingestion.** `automations/scheduler.py` runs daily, pulling fresh team, standings, and match data using APScheduler.

## Tech Stack

Python, SQLAlchemy, SQLite, APScheduler

Planned for later phases: FastAPI, LangChain, RAG chatbot layer

## Project Structure

```
world_cup/
├── data/             # SQLAlchemy models and ingestion scripts, pulling
│                     # live match, team, and standings data from
│                     # football-data.org and api-football.com
├── intelligence/
│   ├── elo.py        # The Elo rating engine, pure functions, no DB calls
│   ├── run_elo_2026.py   # Computes ratings from 2026 match history
│   ├── run_elo_2022.py   # Computes ratings from 2022 match history (backtest)
│   └── recompute.py  # Rebuilds form, standings, and ratings after each result
├── automations/
│   └── scheduler.py   # Runs daily ingestion on a schedule
├── config.py          # Environment and database configuration
├── worldcup.db        # 2022 backtest database
└── worldcup_2026.db   # Live 2026 database 

```
The full technical write up, covering data sourcing, schema design, the Elo formula, and every data quality issue found along the way, is available here: *[https://medium.com/@terrymigwi/tournamentiq-8e46684d7cf7]*