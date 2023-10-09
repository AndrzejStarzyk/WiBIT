from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from recommending_v2.model.point_of_interest import PointOfInterest


class Provider:
    def __init__(self):
        self.pois = []
        self.fetched = False
        self.mongodb_uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    def fetch_pois(self):
        client = MongoClient(self.mongodb_uri, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["cracow-attractions-v2"]


        """overpass = Overpass()
        nominatim = Nominatim()

        cracow = nominatim.query('Kraków, Poland')
        selectors = [['"tourism"="museum"'],
                     ['"tourism"="gallery"'],
                     ['"tourism"="aquarium"'],
                     ['"tourism"="artwork"'],
                     ['"tourism"="theme_park"'],
                     ['"tourism"="viewpoint"'],
                     ['"tourism"="zoo"'],
                     ['"heritage"="2"'],
                     ['"historic"="building"'],
                     ['"historic"="castle"'],
                     ['"historic"="city_gate"'],
                     ['"leisure"="firepit"'],
                     ['"leisure"="fishing"'],
                     ['"leisure"="garden"'],
                     ['"leisure"="water_park"'],
                     ['"memorial"="statue"'],
                     ['"military"="bunker"'],
                     ['"natural"="peak"']]

        for selector in selectors[0:3]:
            query = overpassQueryBuilder(area=cracow.areaId(), elementType=['node', 'way'], selector=selector,
                                         out='body')
            res = overpass.query(query)
            for element in res.elements():
                osm = f"{element.type()}/{element.id()}"
                el = collection.find_one({"osm": osm})
                if el is not None:
                    """
        all_places = collection.find()

        for place in all_places:
            self.pois.append(
                PointOfInterest(name=place.get('name'),
                                lon=place.get('point').get('lon'),
                                lat=place.get('point').get('lat'),
                                kinds=place.get('kinds'),
                                xid=place.get('xid'),
                                website=place.get('url'),
                                wiki=place.get('wikipedia'),
                                img=place.get('image'),
                                opening_hours=place.get('opening_hours')))

        self.fetched = True

    def get_places(self):
        if not self.fetched:
            self.fetch_pois()
        return self.pois


if __name__ == "__main__":
    provider = Provider()
    places = provider.get_places()
    print(places[0])
