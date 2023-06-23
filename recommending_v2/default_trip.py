from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

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
        self.places = []
        self.places_fetched = False
        self.uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"
        self.default_trip = []
    def get_trip(self):
        client = MongoClient(self.uri, server_api=ServerApi('1'))

        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["cracow-attractions"]

        for osm in trip["trip"]:
            place = collection.find_one({"osm": f"{osm['type']}/{osm['id']}"})
            if place is not None:
                lon = place['point']['lon']
                lat = place['point']['lat']
                self.default_trip.append((lon, lat, place["name"]))

        return self.default_trip
