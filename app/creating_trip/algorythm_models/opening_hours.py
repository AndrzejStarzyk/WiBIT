from typing import List, Union
from datetime import time
from humanized_opening_hours import OHParser
from re import compile


class BeginningOrEnding:
    def __init__(self, day: int, time_str: str):
        self.day: int = day + 1
        self.time: time = time.fromisoformat(f"{time_str[0:2]}:{time_str[3:5]}:00")

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
        if len(periods) == 0:
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
    if opening_hours_db is None:
        return OpeningHours([])

    try:
        parser = OHParser(opening_hours_db)
        day_regex = compile("^(\w+):\s*(?:(\d\d:\d\d)\s*-\s*(\d\d:\d\d)|(closed))$")
        days = parser.render().get_human_names().get('days')

        parser = OHParser(opening_hours_db)
        description = parser.render().plaintext_week_description()
        week = description.split("\n")

        periods = []
        for day in week:
            match = day_regex.match(day)
            if match is None:
                continue
            if match.group(4) is None:
                start = BeginningOrEnding(day=days.index(match.group(1)), time_str=match.group(2))
                end = BeginningOrEnding(day=days.index(match.group(1)), time_str=match.group(3))
                periods.append(Period(start, end))

        return OpeningHours(periods)
    except Exception as e:
        return OpeningHours([])
