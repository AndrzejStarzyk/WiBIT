from datetime import timedelta, date
from typing import Union


class ScheduleParameters:
    def __init__(self):
        self.start_day: Union[int, None] = None
        self.start_month: Union[int, None] = None
        self.end_day: Union[int, None] = None
        self.end_month: Union[int, None] = None
        self.start_date: Union[date, None] = None
        self.end_date: Union[date, None] = None

    def assume_missing_info(self):
        today = date.today()

        if self.end_month is None:
            if self.start_month is None:
                if self.end_day is None:
                    if self.start_day is None:
                        end = today + timedelta(days=7)
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
                end = today + timedelta(days=7)
            else:
                start = date(day=self.start_day, month=month, year=year)
                end = today + timedelta(days=7)
        else:
            if self.start_day is None:
                end = date(day=self.end_day, month=month, year=year)
                start = today - timedelta(days=7)
            else:
                if is_start:
                    start = date(day=self.start_day, month=month, year=year)
                    if self.end_day > self.start_day:
                        end = date(day=self.end_day, month=month, year=year)
                    else:
                        if month == 12:
                            end = date(day=self.end_day, month=1, year=year + 1)
                        else:
                            end = date(day=self.end_day, month=month + 1, year=year)
                else:
                    end = date(day=self.end_day, month=month, year=year)
                    if self.end_day > self.start_day:
                        start = date(day=self.start_day, month=month, year=year)
                    else:
                        if month == 1:
                            start = date(day=self.start_day, month=12, year=year - 1)
                        else:
                            start = date(day=self.start_day, month=month - 1, year=year)
        self.start_date = start
        self.end_date = end

    def both_month_given(self, month1, month2):
        if month1 == month2:
            self.month_given(month1, True)
        else:
            today = date.today()
            if month1 < month2:
                if today.month <= month1:
                    year1 = today.year
                    year2 = today.year
                else:
                    year1 = today.year + 1
                    year2 = today.year + 1
            else:
                if today.month <= month1:
                    year1 = today.year
                    year2 = today.year + 1
                else:
                    year1 = today.year + 1
                    year2 = today.year + 2
            if self.end_day is None:
                if self.start_day is None:
                    start = date(day=27, month=month1, year=year1)
                    end = date(day=2, month=month2, year=year2)
                else:
                    start = date(day=self.start_day, month=month1, year=year1)
                    end = date(day=2, month=month2, year=year2)
            else:
                if self.start_day is None:
                    end = date(day=self.end_day, month=month2, year=year2)
                    start = date(day=27, month=month1, year=year1)
                else:
                    start = date(day=self.start_day, month=month1, year=year1)
                    end = date(day=self.end_day, month=month2, year=year2)
            self.start_date = start
            self.end_date = end

    def day_given(self, day: int, is_start: bool):
        today = date.today()
        if is_start:
            if day >= today.day:
                start = today + timedelta(days=(day - today.day))
                end = start + timedelta(days=7)
            else:
                if today.month == 12:
                    start = date(day=day, month=1, year=today.year + 1)
                    end = start + timedelta(days=7)
                else:
                    start = date(day=day, month=today.month + 1, year=today.year)
                    end = start + timedelta(days=7)
        else:
            if day >= today.day:
                end = today + timedelta(days=(day - today.day))
                start = end - timedelta(days=7)
            else:
                if today.month == 12:
                    end = date(day=day, month=1, year=today.year + 1)
                    start = end - timedelta(days=7)
                else:
                    end = date(day=day, month=today.month + 1, year=today.year)
                    start = end - timedelta(days=7)
        self.start_date = start
        self.end_date = end

    def both_days_given(self, day1, day2):
        today = date.today()
        if day1 <= day2:
            if today.day <= day1:
                start = date(day=day1, month=today.month, year=today.year)
                end = date(day=day2, month=today.month, year=today.year)
            else:
                if today.month == 12:
                    start = date(day=day1, month=1, year=today.year + 1)
                    end = date(day=day2, month=1, year=today.year + 1)
                else:
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
