from datetime import datetime

from recommending_v2.algorythm_models.mongo_trip_models import ScheduleMongo, PoiMongo, DayMongo, TripDaysMongo
from schedule import Schedule
from models.mongo_utils import MongoUtils


def save_trip(user_id, schedule: Schedule):
    mongo_utils = MongoUtils()
    trips = mongo_utils.get_collection('trips')

    for event in schedule.trajectories[0].get_events():
        print(event.start)
        print(type(event.start))

    trip = TripDaysMongo(
        user_id=user_id,
        days=[DayMongo(
            schedule=ScheduleMongo(
                date=schedule.schedule[i].date_str,
                start=schedule.schedule[i].start,
                end=schedule.schedule[i].end
            ),
            trajectory=[
                PoiMongo(
                    poi_id=event.poi.xid,
                    plan_from=datetime.combine(datetime.date(schedule.schedule[i].start), event.start),
                    plan_to=datetime.combine(datetime.date(schedule.schedule[i].start), event.end),
                ) for event in schedule.trajectories[i].get_events()]
        ) for i in range(schedule.days)]
    )

    print(trip.to_bson())

    trips.insert_one(trip.to_bson())

