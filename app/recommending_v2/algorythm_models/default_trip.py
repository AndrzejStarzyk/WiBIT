import datetime
from datetime import timedelta, date
from typing import List, Union, Tuple

from models.mongo_utils import MongoUtils
from recommending_v2.algorythm_models.schedule import Day, Schedule
from recommending_v2.algorythm_models.trajectory import Trajectory
from recommending_v2.point_of_interest.point_of_interest import PointOfInterest

trip = {
    "trip": [
        {
            "id": 85151350,
            "type": "way"
        },
        {
            "id": 2518857,
            "type": "rel"
        },
        {
            "id": 396000369,
            "type": "way"
        },
        {
            "id": 2270819,
            "type": "rel"
        },
        {
            "id": 278057698,
            "type": "node"
        },
        {
            "id": 104374972,
            "type": "way"
        },
        {
            "id": 200358351,
            "type": "way"
        },
        {
            "id": 214263,
            "type": "rel"
        },
        {
            "id": 26195267,
            "type": "way"
        },
        {
            "id": 39357538,
            "type": "way"
        },
    ]
}

trip2 = [
    ("W233371578", timedelta(hours=2)),
    ("Q11806796", timedelta(hours=1)),
    ("R2270819", timedelta(hours=1)),
    ("N1332080339", timedelta(hours=2))]


def get_default_places_xid() -> List[str]:
    return list(map(lambda x: x[0], trip2))


today = Day(date.today().isoformat(), "10:00", "18:00")


class DefaultTrip:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection = db_connection
        self.places: List[Tuple[PointOfInterest, timedelta]] = []

        self.fetch_trip()

    def fetch_trip(self):
        collection = self.db_connection.get_collection_attractions("poland-cracow")

        for xid, time in trip2:
            place = collection.find_one({"xid": xid})
            if place is not None:
                self.places.append((PointOfInterest(name=place.get('name'),
                                                    lon=place.get('point').get('lon'),
                                                    lat=place.get('point').get('lat'),
                                                    kinds=place.get('kinds'),
                                                    xid=place.get('xid'),
                                                    website=place.get('url'),
                                                    wiki=place.get('wikipedia'),
                                                    opening_hours=place.get('opening_hours')), time))

    def get_trip(self, day: Union[Day, None]):
        if day is None:
            day = today
        trajectory = Trajectory()
        travel = timedelta(minutes=15)
        start = day.start
        for place, time in self.places:
            trajectory.add_event(place, start, start + travel)
            start += travel + time
        return trajectory

    def get_default_schedule(self):

        fill1 = ''
        fill2 = ''

        if today.start.minute < 10:
            fill1 = '0'
        if today.end.minute < 10:
            fill2 = '0'
        print([(f"{today.start.hour}:{fill1}{today.start.minute}",
                f"{today.end.hour}:{fill2}{today.end.minute}")])
        return Schedule(1,
                        [today.date_str],
                        [(f"{today.start.hour}:{fill1}{today.start.minute}",
                          f"{today.end.hour}:{fill2}{today.end.minute}")])


if __name__ == "__main__":
    d = datetime.date.today()
    print(d.isoformat())
