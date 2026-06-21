from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey
from typing import Optional

class Base(DeclarativeBase):
    pass

class Team(Base):
    __tablename__="teams"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=False)
    name:Mapped[str] = mapped_column()
    code:Mapped[str] = mapped_column()
    country:Mapped[str]=mapped_column()
    founded: Mapped[Optional[int]]=mapped_column()
    national:Mapped[bool]=mapped_column()
    logo:Mapped[str]=mapped_column()
    venue_name:Mapped[str]=mapped_column()
    venue_city:Mapped[str]=mapped_column()
    venue_capacity:Mapped[Optional[int]]=mapped_column()

class GroupStandings(Base):
    __tablename__="groupstandings"
    id: Mapped[int]=mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    group_name: Mapped[str]=mapped_column()
    rank: Mapped[int]=mapped_column()
    points: Mapped[int]=mapped_column()
    goals_diff: Mapped[int]=mapped_column()
    played: Mapped[int]=mapped_column()
    won: Mapped[int]=mapped_column()
    drawn: Mapped[int]=mapped_column()
    lost: Mapped[int]=mapped_column()
    goals_for: Mapped[int]=mapped_column()
    goals_against: Mapped[int]=mapped_column()

class Match(Base):
    __tablename__="matches"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    date: Mapped[str] = mapped_column()
    round: Mapped[str]=mapped_column()
    venue_name: Mapped[Optional[str]]=mapped_column()
    venue_city: Mapped[Optional[str]]=mapped_column()
    status: Mapped[str]=mapped_column()
    home_goals: Mapped[Optional[int]]=mapped_column()
    away_goals: Mapped[Optional[int]]=mapped_column()
    home_goals_ht: Mapped[Optional[int]]=mapped_column()
    away_goals_ht: Mapped[Optional[int]]=mapped_column()
    penalty_home: Mapped[Optional[int]]=mapped_column()
    penalty_away: Mapped[Optional[int]]=mapped_column()

