from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

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


class DefaultTrip:
    def __init__(self):
        self.trip: Trajectory = Trajectory()
        self.places_fetched: bool = False
        self.uri: str = "mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    def get_trip(self):
        client = MongoClient(self.uri, server_api=ServerApi('1'))

        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["cracow-attractions-popular"]

        for osm in trip["trip"]:
            place = collection.find_one({"osm": f"{osm['type']}/{osm['id']}"})
            if place is not None:
                self.trip.add_poi(PointOfInterest(name=place.get('name'),
                                                  lon=place.get('point').get('lon'),
                                                  lat=place.get('point').get('lat'),
                                                  kinds=place.get('kinds'),
                                                  xid=place.get('xid'),
                                                  website=place.get('url'),
                                                  wiki=place.get('wikipedia'),
                                                  img=place.get('image'),
                                                  opening_hours=place.get('opening_hours')))

        return self.trip
