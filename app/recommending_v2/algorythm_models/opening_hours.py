from typing import List, Union
from datetime import time


class BeginningOrEnding:
    def __init__(self, day: int, time_str: str):
        self.day: int = day + 1
        self.time: time = time.fromisoformat(f"{time_str[0:2]}:{time_str[2:4]}:00")

    def __str__(self):
        return str(self.day) + " " + str(self.time.isoformat())


class Period:
    def __init__(self, opening: BeginningOrEnding, closing: Union[BeginningOrEnding, None]):
        self.open = opening
        self.close = closing

    def __str__(self):
        if self.close is None:
            return str(self.open)
        if self.open.day == self.close.day:
            return str(self.open.time) + " - " + str(self.close.time)
        return str(self.open) + " - " + str(self.close)


class OpeningHours:
    def __init__(self, periods: List[Period]):
        if len(periods) == 1 and \
                periods[0].close is None and \
                periods[0].open.day == 1 and \
                periods[0].open.time == time():
            self.periods = []
            self.is_always_opened = True
        else:
            self.periods = periods
            self.is_always_opened = False

    def __str__(self):
        if self.is_always_opened:
            return "Always Opened"
        res = "Opening hours: "
        for period in self.periods:
            res += str(period) + ", "

        return res[0:-2]

    def is_open(self, weekday: int, start: time, end: time):
        if self.is_always_opened:
            return True
        for period in self.periods:
            if period.open.day == weekday and period.open.time <= end and \
                    period.close.day == weekday and period.close.time >= start:
                return True
        return False


def parse_opening_hours(opening_hours_db) -> OpeningHours:
    periods = []
    for period_db in opening_hours_db:
        start = BeginningOrEnding(period_db.get('open').get('day'), period_db.get('open').get('time'))
        end = None
        if 'close' in period_db:
            end = BeginningOrEnding(period_db.get('close').get('day'), period_db.get('close').get('time'))
        periods.append(Period(start, end))
    return OpeningHours(periods)


if __name__ == "__main__":
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi

    client = MongoClient("mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority",
                         server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    collection = db["cracow-attractions-popular"]

    attraction = collection.find_one({'name': "Dom kultury"})

    opening_hours = parse_opening_hours(attraction.get('opening_hours'))
    print(attraction)
    print(opening_hours)
