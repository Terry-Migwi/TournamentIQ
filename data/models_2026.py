from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey
from typing import Optional

class Base(DeclarativeBase):
    pass

class Team(Base):
    __tablename__="teams"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=False)
    name:Mapped[str] = mapped_column()
    tla:Mapped[str] = mapped_column()
    founded: Mapped[Optional[int]]=mapped_column()
    crest:Mapped[str]=mapped_column()
    venue:Mapped[Optional[str]]=mapped_column()

class GroupStandings(Base):
    __tablename__="group_standings"
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    group_name: Mapped[str]=mapped_column()
    position: Mapped[int]=mapped_column()
    played: Mapped[int]=mapped_column()
    won: Mapped[int]=mapped_column()
    drawn: Mapped[int]=mapped_column()
    lost: Mapped[int]=mapped_column()
    points: Mapped[int]=mapped_column()
    goals_for: Mapped[int]=mapped_column()
    goals_against: Mapped[int]=mapped_column()
    goals_diff: Mapped[int]=mapped_column()
    form: Mapped[Optional[str]] = mapped_column()

class Match(Base):
    __tablename__="matches"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=False)
    home_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    season: Mapped[int] = mapped_column()
    stage: Mapped[str] = mapped_column()
    matchday: Mapped[Optional[int]] = mapped_column()
    date: Mapped[Optional[str]] = mapped_column()
    status: Mapped[str]=mapped_column()
    duration: Mapped[Optional[str]]=mapped_column()
    home_goals: Mapped[Optional[int]]=mapped_column()
    away_goals: Mapped[Optional[int]]=mapped_column()
    home_goals_ht: Mapped[Optional[int]]=mapped_column()
    away_goals_ht: Mapped[Optional[int]]=mapped_column()

class EloRating(Base):
    __tablename__ = "elo_ratings"
    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    stage: Mapped[str] = mapped_column()
    rating_before: Mapped[float] = mapped_column()
    rating_after: Mapped[float] = mapped_column()