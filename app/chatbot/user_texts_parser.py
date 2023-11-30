from datetime import date, timedelta

from recommending_v3.date_recognition import parse_date_text
from recommender import Recommender


def parse_user_text(user_information: str, user_date: str, recommender: Recommender):
    schedule_parameters = parse_date_text(user_date)

    start_date: date = schedule_parameters.start_date
    dates = []
    tmp = start_date
    i = 0
    while tmp != schedule_parameters.end_date:
        tmp = start_date + timedelta(days=i)
        dates.append(tmp.isoformat())
        i += 1

    recommender.dates = dates
    recommender.days = len(dates)

    schedule_hours = [('10:00', '18:00')
                      for _ in range(0, len(dates))]
    recommender.hours = schedule_hours
    recommender.create_schedule()
