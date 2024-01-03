from datetime import timedelta, date
from calendar import monthrange
from typing import Union


def validate_day(year, month, day) -> int:
    _, days_nr = monthrange(year, month)
    if day > days_nr:
        return day % 10
    return day


class ScheduleParameters:
    def __init__(self):
        self.start_day: Union[int, None] = None
        self.start_month: Union[int, None] = None
        self.end_day: Union[int, None] = None
        self.end_month: Union[int, None] = None
        self.schedule_length: int = 7

        self.start_date: Union[date, None] = None
        self.end_date: Union[date, None] = None

    def assume_missing_info(self):
        today = date.today()

        if self.end_month is not None and self.end_month > 12:
            self.end_month = (self.end_month - 1) % 12 + 1
        if self.start_month is not None and self.start_month > 12:
            self.start_month = (self.start_month - 1) % 12 + 1

        if self.end_month is None:
            if self.start_month is None:
                if self.end_day is None:
                    if self.start_day is None:
                        end = today + timedelta(days=self.schedule_length)
                        self.start_date = today
                        self.end_date = end
                    else:
                        self.day_given(self.start_day, True)
                else:
                    if self.start_day is None:
                        self.day_given(self.end_day, False)
                    else:
                        self.both_days_given(self.start_day, self.end_day)
            else:
                if self.end_month is None:
                    self.month_given(self.start_month, True)
        else:
            if self.start_month is None:
                self.month_given(self.end_month, False)
            else:
                self.both_month_given(self.start_month, self.end_month)

    def month_given(self, month: int, is_start: bool):
        today = date.today()
        if month >= today.month:
            year = today.year
        else:
            year = today.year + 1

        if self.end_day is None:
            if self.start_day is None:
                start = date(day=1, month=month, year=year)
                end = today + timedelta(days=self.schedule_length)
            else:
                self.start_day = validate_day(year, month, self.start_day)
                start = date(day=self.start_day, month=month, year=year)
                end = date(day=self.start_day, month=month, year=year)
        else:
            if self.start_day is None:
                self.end_day = validate_day(year, month, self.end_day)
                end = date(day=self.end_day, month=month, year=year)
                start = date(day=self.end_day, month=month, year=year)
            else:
                if is_start:
                    self.start_day = validate_day(year, month, self.start_day)
                    start = date(day=self.start_day, month=month, year=year)
                    if self.end_day > self.start_day:
                        self.end_day = validate_day(year, month, self.end_day)
                        end = date(day=self.end_day, month=month, year=year)
                    else:
                        if month == 12:
                            self.end_day = validate_day(year + 1, 1, self.end_day)
                            end = date(day=self.end_day, month=1, year=year + 1)
                        else:
                            self.end_day = validate_day(year, month + 1, self.end_day)
                            end = date(day=self.end_day, month=month + 1, year=year)
                else:
                    self.end_day = validate_day(year, month, self.end_day)
                    end = date(day=self.end_day, month=month, year=year)
                    if self.end_day > self.start_day:
                        self.start_day = validate_day(year, month, self.start_day)
                        start = date(day=self.start_day, month=month, year=year)
                    else:
                        if month == 1:
                            self.start_day = validate_day(year - 1, 12, self.start_day)
                            start = date(day=self.start_day, month=12, year=year - 1)
                        else:
                            self.start_day = validate_day(year, month - 1, self.start_day)
                            start = date(day=self.start_day, month=month - 1, year=year)
        self.start_date = start
        self.end_date = end

    def both_month_given(self, month1, month2):
        today = date.today()
        if month1 > month2:
            month1, month2 = month2, month1
        if today.month <= month1:
            year1 = today.year
            year2 = today.year
        else:
            year1 = today.year + 1
            year2 = today.year + 1

        if self.end_day is None:
            if self.start_day is None:
                if month1 == month2:
                    start = date(day=1, month=month1, year=year1)
                    end = date(day=6, month=month2, year=year2)
                else:
                    start = date(day=27, month=month1, year=year1)
                    end = date(day=2, month=month2, year=year2)
            else:
                self.start_day = validate_day(year1, month1, self.start_day)
                start = date(day=self.start_day, month=month1, year=year1)
                end = date(day=2, month=month2, year=year2)
        else:
            self.end_day = validate_day(year2, month2, self.end_day)
            if self.start_day is None:
                start = date(day=27, month=month1, year=year1)
                end = date(day=self.end_day, month=month2, year=year2)
            else:
                self.start_day = validate_day(year1, month1, self.start_day)
                start = date(day=self.start_day, month=month1, year=year1)
                end = date(day=self.end_day, month=month2, year=year1)
        self.start_date = start
        self.end_date = end

    def day_given(self, day: int, is_start: bool):
        today = date.today()
        day = validate_day(today.year, 1, day)

        if is_start:
            if day >= today.day:
                start = today + timedelta(days=(day - today.day))
                end = start + timedelta(days=self.schedule_length)
            else:
                if today.month == 12:
                    start = date(day=day, month=1, year=today.year + 1)
                    end = start + timedelta(days=self.schedule_length)
                else:
                    day = validate_day(today.year, today.month + 1, day)
                    start = date(day=day, month=today.month + 1, year=today.year)
                    end = start + timedelta(days=self.schedule_length)
        else:
            if day >= today.day:
                end = today + timedelta(days=(day - today.day))
                start = end - timedelta(days=self.schedule_length)
            else:
                if today.month == 12:
                    end = date(day=day, month=1, year=today.year + 1)
                    start = end - timedelta(days=self.schedule_length)
                else:
                    day = validate_day(today.year, today.month + 1, day)
                    end = date(day=day, month=today.month + 1, year=today.year)
                    start = end - timedelta(days=self.schedule_length)
        self.start_date = start
        self.end_date = end

    def both_days_given(self, day1, day2):
        today = date.today()
        day1 = validate_day(today.year, 1, day1)
        day2 = validate_day(today.year, 1, day2)

        if day1 <= day2:
            if today.day <= day1:
                start = date(day=day1, month=today.month, year=today.year)
                end = date(day=day2, month=today.month, year=today.year)
            else:
                if today.month == 12:
                    start = date(day=day1, month=1, year=today.year + 1)
                    end = date(day=day2, month=1, year=today.year + 1)
                else:
                    day1 = validate_day(today.year, today.month + 1, day1)
                    day2 = validate_day(today.year, today.month + 1, day2)
                    start = date(day=day1, month=today.month + 1, year=today.year)
                    end = date(day=day2, month=today.month + 1, year=today.year)
        else:
            if today.day <= day1:
                start = date(day=day1, month=today.month, year=today.year)
                if today.month == 12:
                    end = date(day=day2, month=1, year=today.year + 1)
                else:
                    end = date(day=day2, month=today.month + 1, year=today.year)
            else:
                if today.month == 12:
                    start = date(day=day1, month=1, year=today.year + 1)
                else:
                    start = date(day=day1, month=today.month + 1, year=today.year)
                if today.month == 11:
                    end = date(day=day2, month=1, year=today.year + 1)
                elif today.month == 12:
                    end = date(day=day2, month=2, year=today.year + 1)
                else:
                    end = date(day=day2, month=today.month + 2, year=today.year)

        self.start_date = start
        self.end_date = end
