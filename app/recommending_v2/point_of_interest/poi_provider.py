import re
from typing import List, Tuple
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

from recommending_v2.point_of_interest.point_of_interest import PointOfInterest
from recommending_v2.point_of_interest.poi_from_osm_selectors import selectors
from models.mongo_utils import MongoUtils
from recommending_v2.utils import dist

max_dist = 2000


class PoiProvider:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection = db_connection

        self.pois: List[PointOfInterest] = []
        self.available_attractions_sets: List[str] = []

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
            self.available_attractions_sets.append(f'{data.get("country")}-{data.get("city")}')

        self.available_fetched = True

    def fetch_pois(self, country_region):
        if self.fetched:
            return

        if country_region in self.available_attractions_sets:
            collection = self.db_connection.get_collection_attractions(f"{country_region}")
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

        else:
            regex = re.compile("^(\w)+_(\w)+$")
            match = regex.match(country_region)
            self.fetch_attractions_from_osm(match.group(2))

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
        nominatim = Nominatim()
        region = nominatim.query(f"{region}")

        overpass = Overpass()
        query_str = '[out:json][timeout:25];{{geocodeArea:{' + region + '}}}->.searchArea;('
        for selector in selectors:
            query_str += f'nwr["{selector[0]}"="{selector[1]}"](area.searchArea);'

        query_str += ');out body;>;out skel;'
        query = overpassQueryBuilder(query_str)
        res = overpass.query(query)
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
                                img=place.get('tags').get('image'),
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
        if not self.fetched:
            self.fetch_pois()
        return self.pois

    def get_available_attraction_sets(self) -> List[Tuple[str, str]]:
        if not self.available_fetched:
            self.fetch_available_attraction_sets()
        return self.available_attractions_sets

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
