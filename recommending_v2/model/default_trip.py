from datetime import timedelta, datetime
from typing import List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from recommending_v2.model.schedule import Day
from recommending_v2.model.trajectory import Trajectory
from recommending_v2.model.point_of_interest import PointOfInterest

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
    ("W25171269", timedelta(hours=2)),
    ("Q11806796", timedelta(hours=1)),
    ("R2270819", timedelta(hours=1)),
    ("N1332080339", timedelta(hours=2))]


def get_default_places_xid() -> List[str]:
    return list(map(lambda x: x[0], trip2))


class DefaultTrip:
    def __init__(self):
        self.trip: Trajectory = Trajectory()
        self.places_fetched: bool = False
        self.uri: str = "mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    def get_trip(self, day: Day) -> Trajectory:
        client = MongoClient(self.uri, server_api=ServerApi('1'))

        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["cracow-attractions-v2"]
        travel = timedelta(minutes=15)
        start = day.start
        for xid, time in trip2:
            place = collection.find_one({"xid": xid})
            if place is not None:
                self.trip.add_event(PointOfInterest(name=place.get('name'),
                                                    lon=place.get('point').get('lon'),
                                                    lat=place.get('point').get('lat'),
                                                    kinds=place.get('kinds'),
                                                    xid=place.get('xid'),
                                                    website=place.get('url'),
                                                    wiki=place.get('wikipedia'),
                                                    img=place.get('image'),
                                                    opening_hours=place.get('opening_hours')),
                                    start, start + travel)
                start += travel + time

        return self.trip
