from typing import List, Tuple
from datetime import date, time, datetime

from recommending_v2.model.point_of_interest import PointOfInterest


class Event:
    def __init__(self, start: time, end: time, poi: PointOfInterest):
        self.start: time = start
        self.end: time = end
        self.poi: PointOfInterest = poi


class Day:
    def __init__(self, date_str: str, start: str, end: str):
        start = time.fromisoformat(f"{start[0:2]}:{start[3:5]}:00")
        end = time.fromisoformat(f"{end[0:2]}:{end[3:5]}:00")
        date_ = date.fromisoformat(date_str)

        self.date_str: str = date_str
        self.start: datetime = datetime.combine(date_, start)
        self.end: datetime = datetime.combine(date_, end)
        self.weekday: int = date_.weekday()
        self.events: List[Event] = []

    def add_event(self, start: time, end: time, poi: PointOfInterest):
        self.events.append(Event(start, end, poi))


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
