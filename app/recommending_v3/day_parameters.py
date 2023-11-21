from datetime import timedelta, date


class DayParameters:
    def __init__(self):
        self.start_day = None
        self.start_month = None
        self.end_day = None
        self.end_month = None
        self.start_date = None
        self.end_date = None

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
                start = date(1, month, year)
                end = today + timedelta(days=7)
            else:
                start = date(self.start_day, month, year)
                end = today + timedelta(days=7)
        else:
            if self.start_day is None:
                end = date(self.end_day, month, year)
                start = today - timedelta(days=7)
            else:
                if is_start:
                    start = date(self.start_day, month, year)
                    if self.end_day > self.start_day:
                        end = date(self.end_day, month, year)
                    else:
                        if month == 12:
                            end = date(self.end_day, 1, year + 1)
                        else:
                            end = date(self.end_day, month + 1, year)
                else:
                    end = date(self.end_day, month, year)
                    if self.end_day > self.start_day:
                        start = date(self.start_day, month, year)
                    else:
                        if month == 1:
                            start = date(self.start_day, 12, year - 1)
                        else:
                            start = date(self.start_day, month - 1, year)
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
                    start = date(27, month1, year1)
                    end = date(2, month2, year2)
                else:
                    start = date(self.start_day, month1, year1)
                    end = date(2, month2, year2)
            else:
                if self.start_day is None:
                    end = date(self.end_day, month2, year2)
                    start = date(27, month1, year1)
                else:
                    start = date(self.start_day, month1, year1)
                    end = date(self.end_day, month2, year2)
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
                    start = date(day, 1, today.year + 1)
                    end = start + timedelta(days=7)
                else:
                    start = date(day, today.month + 1, today.year)
                    end = start + timedelta(days=7)
        else:
            if day >= today.day:
                end = today + timedelta(days=(day - today.day))
                start = end - timedelta(days=7)
            else:
                if today.month == 12:
                    end = date(day, 1, today.year + 1)
                    start = end - timedelta(days=7)
                else:
                    end = date(day, today.month + 1, today.year)
                    start = end - timedelta(days=7)
        self.start_date = start
        self.end_date = end

    def both_days_given(self, day1, day2):
        today = date.today()
        if day1 <= day2:
            if today.day <= day1:
                start = date(day1, today.month, today.year)
                end = date(day2, today.month, today.year)
            else:
                if today.month == 12:
                    start = date(day1, 1, today.year + 1)
                    end = date(day2, 1, today.year + 1)
                else:
                    start = date(day1, today.month + 1, today.year)
                    end = date(day2, today.month + 1, today.year)
        else:
            if today.day <= day1:
                start = date(day1, today.month, today.year)
                if today.month == 12:
                    end = date(day2, 1, today.year + 1)
                else:
                    end = date(day2, today.month + 1, today.year)
            else:
                if today.month == 12:
                    start = date(day1, 1, today.year + 1)
                else:
                    start = date(day1, today.month + 1, today.year)
                if today.month == 11:
                    end = date(day2, 1, today.year + 1)
                elif today.month == 12:
                    end = date(day2, 2, today.year + 1)
                else:
                    end = date(day2, today.month + 2, today.year)

        self.start_date = start
        self.end_date = end
