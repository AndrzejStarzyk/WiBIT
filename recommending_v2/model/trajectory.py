from datetime import time, datetime
from typing import List

from recommending_v2.model.point_of_interest import PointOfInterest


class Event:
    def __init__(self, start: time, end: time, poi: PointOfInterest):
        self.start: time = start
        self.end: time = end
        self.poi: PointOfInterest = poi


class Trajectory:
    def __init__(self):
        self.events: List[Event] = []

    def add_event(self, poi: PointOfInterest, from_time: datetime, to_time: datetime):
        self.events.append(Event(from_time.time(), to_time.time(), poi))

    def get_pois(self):
        return list(map(lambda x: x.poi, self.events))
