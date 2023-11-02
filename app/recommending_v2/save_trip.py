from datetime import datetime

from recommending_v2.algorythm_models.mongo_trip_models import ScheduleMongo, PoiMongo, DayMongo, TripDaysMongo
from schedule import Schedule
from trajectory import Trajectory
from point_of_interest import PointOfInterest
from models.mongo_utils import MongoUtils
from models.constants import ATTRACTIONS_COLLECTION


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


def poi_from_id(poi_id, places):
    place = places.find_one({'xid': poi_id})

    if not place:
        return None

    return PointOfInterest(name=place.get('name'),
                           lon=place.get('point').get('lon'),
                           lat=place.get('point').get('lat'),
                           kinds=place.get('kinds'),
                           xid=place.get('xid'),
                           website=place.get('url'),
                           wiki=place.get('wikipedia'),
                           img=place.get('image'),
                           opening_hours=place.get('opening_hours'))


def schedule_from_saved_trip(saved_trip: TripDaysMongo) -> Schedule:
    mongo_utils = MongoUtils()
    places = mongo_utils.get_collection(ATTRACTIONS_COLLECTION)

    hours = []
    trajectories = []

    for day in saved_trip.days:
        start_str = day.schedule.start.time().strftime('%H:%M')
        end_str = day.schedule.end.time().strftime('%H:%M')
        hours.append((start_str, end_str))

        tmp_trajectory = Trajectory()
        for poi in day.trajectory:
            poi_from_db = poi_from_id(poi.poi_id, places)
            tmp_trajectory.add_event(poi=poi_from_db,
                                     from_time=poi.plan_from,
                                     to_time=poi.plan_to)

        trajectories.append(tmp_trajectory)

    schedule = Schedule(days=len(saved_trip.days),
                        dates=[day.schedule.date for day in saved_trip.days],
                        hours=hours)

    for tmp_trajectory in trajectories:
        schedule.add_trajectory(tmp_trajectory)

    return schedule
