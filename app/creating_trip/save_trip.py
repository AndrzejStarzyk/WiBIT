from datetime import datetime
from typing import List, Union

from creating_trip.poi_provider import PoiProvider
from creating_trip.algorythm_models.mongo_trip_models import ScheduleMongo, PoiMongo, DayMongo, TripDaysMongo
from creating_trip.algorythm_models.schedule import Schedule
from creating_trip.algorythm_models.trajectory import Trajectory
from creating_trip.point_of_interest.point_of_interest import PointOfInterest
from models.mongo_utils import MongoUtils


def save_trip(user_id, schedule: Schedule, region: str):
    mongo_utils = MongoUtils()
    trips = mongo_utils.get_collection('trips')

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
        ) for i in range(schedule.days)],
        region=region
    )

    trips.insert_one(trip.to_bson())


def poi_from_id(poi_id: str, places: List[PointOfInterest]) -> Union[PointOfInterest, None]:
    places = list(filter(lambda x: x.xid == poi_id, places))

    if len(places) <= 0:
        return None

    place = places[0]

    return place


def schedule_from_saved_trip(saved_trip: TripDaysMongo, poi_provider: PoiProvider) -> Schedule:
    poi_provider.fetch_pois(saved_trip.region)
    places = poi_provider.pois

    hours = []
    trajectories = []

    for day in saved_trip.days:
        start_str = day.schedule.start.time().strftime('%H:%M')
        end_str = day.schedule.end.time().strftime('%H:%M')
        hours.append((start_str, end_str))

        tmp_trajectory = Trajectory()
        for poi in day.trajectory:
            tmp_trajectory.add_event(poi=poi_from_id(poi.poi_id, places),
                                     from_time=poi.plan_from,
                                     to_time=poi.plan_to)

        trajectories.append(tmp_trajectory)

    schedule = Schedule(days=len(saved_trip.days),
                        dates=[day.schedule.date for day in saved_trip.days],
                        hours=hours)

    for tmp_trajectory in trajectories:
        schedule.add_trajectory(tmp_trajectory)

    return schedule
