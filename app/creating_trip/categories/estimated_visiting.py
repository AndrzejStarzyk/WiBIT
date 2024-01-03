from datetime import timedelta

from typing import Dict

from models.mongo_utils import MongoUtils
from creating_trip.point_of_interest.point_of_interest import PointOfInterest


default_estimated_time = timedelta(hours=1, minutes=30)


class VisitingTimeProvider:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection = db_connection

        self.code_to_time: Dict[str, timedelta] = {}
        self.fetched = False

        self.fetch_visiting_times()

    def fetch_visiting_times(self):
        collection = self.db_connection.get_collection("categories")

        categories = collection.find()

        for cat in categories:
            visiting_time = cat.get("visiting_time")
            self.code_to_time.setdefault(cat.get("code"),
                                         timedelta(hours=visiting_time.get("hours"), minutes=visiting_time.get("minutes")))

        self.fetched = True

    def get_visiting_time(self, poi: PointOfInterest) -> timedelta:
        if not self.fetched:
            self.fetch_visiting_times()
        avg_time: timedelta = timedelta()
        total = 0
        for code in poi.kinds:
            if code not in self.code_to_time:
                continue
            avg_time += self.code_to_time[code]
            total += 1

        if total != 0:
            avg_time /= total
        else:
            avg_time = default_estimated_time
        return avg_time
