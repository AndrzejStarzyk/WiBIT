import re
from typing import List, Tuple
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass

from recommending_v2.point_of_interest.point_of_interest import PointOfInterest
from recommending_v2.point_of_interest.poi_from_osm_selectors import selectors
from models.mongo_utils import MongoUtils
from recommending_v2.utils import dist

max_dist = 2000


class PoiProvider:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection = db_connection

        self.pois: List[PointOfInterest] = []
        self.available_country_region: List[Tuple[str, str]] = []

        self.groups: List[List[int]] = []
        self.poi_to_group: dict[int: int] = {}

        self.fetched = False
        self.available_fetched = False
        self.divided = False

        self.fetch_available_attraction_sets()

    def fetch_available_attraction_sets(self):
        collection = self.db_connection.get_collection_attractions("available_cities")

        available_regions_names = collection.find()

        for data in available_regions_names:
            self.available_country_region.append((data.get("country"), data.get("city")))

        self.available_fetched = True

    def fetch_pois(self, country_region="poland-kraków"):
        if self.fetched:
            return

        country_region = country_region.lower()
        if country_region in list(map(lambda x: f"{x[0].lower()}-{x[1].lower()}", self.available_country_region)):
            collection = self.db_connection.get_collection_attractions(country_region)
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
                                    opening_hours=place.get('opening_hours')))

        else:
            self.fetch_attractions_from_osm(country_region)

        self.fetched = True
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

    def fetch_attractions_from_osm(self, region):
        overpass = Overpass()
        nominatim = Nominatim()
        region = nominatim.query(region)

        region_data = region
        if isinstance(region, list):
            region_data = region[0]
        region_name = region_data.get("name")

        query_str = f'area["name"="{region_name}"]->.searchArea;('
        for selector in selectors:
            query_str += f'nwr["{selector[0]}"="{selector[1]}"](area.searchArea);'
        query_str += ');out body;>;out skel;'
        res = overpass.query(query_str)

        for place in res.get('elements'):
            kinds = []
            self.pois.append(
                PointOfInterest(name=place.get('tags').get('name'),
                                lon=place.get('lon'),
                                lat=place.get('lat'),
                                kinds=kinds,
                                xid=f"{place.get('type')[0]}/{place.get('id')}",
                                website=place.get('website'),
                                wiki=place.get('tags').get('wikipedia'),
                                opening_hours=place.get('tags').get('opening_hours')))




    def divide_places(self):
        if self.divided:
            return
        if not self.fetched:
            self.fetch_pois()

        n = len(self.pois)
        visited = [False for _ in range(n)]

        def dfs(v):
            visited[v] = True
            self.groups[curr_group].append(v)
            self.poi_to_group.setdefault(v, curr_group)
            for u in range(n):
                d = dist(self.pois[v], self.pois[u])
                if u != v and not visited[u] and d <= max_dist:
                    dfs(u)

        curr_group = -1
        for i in range(n):
            if not visited[i]:
                curr_group += 1
                self.groups.append([])
                dfs(i)

        self.divided = True

    def get_places(self) -> List[PointOfInterest]:
        return self.pois

    def get_available_attraction_sets(self) -> List[Tuple[str, str]]:
        if not self.available_fetched:
            self.fetch_available_attraction_sets()
        return self.available_country_region

    def get_groups(self):
        if not self.fetched:
            self.fetch_pois()
        if not self.divided:
            self.divide_places()
        return self.groups

    def get_poi_to_group_mapping(self):
        if not self.fetched:
            self.fetch_pois()
        if not self.divided:
            self.divide_places()
        return self.poi_to_group


if __name__ == "__main__":
    provider = PoiProvider()
    provider.divide_places()
    for x in provider.groups:
        if len(x) < 30:
            for y in x:
                print(provider.pois[y].name, provider.pois[y].xid)
        print("--------------------------------------------------------------------")
    print(len(provider.groups))
