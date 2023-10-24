from typing import List, Tuple
from datetime import date, time, datetime

from trajectory import Trajectory


class Day:
    def __init__(self, date_str: str, start: str, end: str):
        start = time.fromisoformat(f"{start[0:2]}:{start[3:5]}:00")
        end = time.fromisoformat(f"{end[0:2]}:{end[3:5]}:00")
        date_ = date.fromisoformat(date_str)

        self.date_str: str = date_str
        self.start: datetime = datetime.combine(date_, start)
        self.end: datetime = datetime.combine(date_, end)
        self.weekday: int = date_.weekday()


class Schedule:
    def __init__(self, days: int, dates: List[str], hours: List[Tuple[str, str]]):
        self.days: int = days
        self.dates: List[str] = dates
        self.hours: List[Tuple[str, str]] = hours
        if self.days != len(self.dates) or self.days != len(self.hours):
            schedule = []
        else:
            schedule = [Day(dates[i], hours[i][0], hours[i][1]) for i in range(self.days)]
        self.schedule: List[Day] = schedule
        self.trajectories: List[Trajectory] = []

    def add_trajectory(self, trajectory: Trajectory):
        self.trajectories.append(trajectory)
