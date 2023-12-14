from typing import List, Tuple, Union
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass

from models.mongo_utils import MongoUtils
from recommending_v2.point_of_interest.mappings_for_OSM import determine_kinds
from recommending_v2.point_of_interest.point_of_interest import PointOfInterest
from recommending_v2.point_of_interest.poi_from_osm_selectors import selectors
from recommending_v2.point_of_interest.region import Region


class PoiProvider:
    def __init__(self, db_connection: MongoUtils):
        self.db_connection: MongoUtils = db_connection

        self.pois: List[PointOfInterest] = []
        self.available_regions: List[Region] = []
        self.available_country_region: List[str] = []
        self.available_region_names: List[str] = []

        self.groups: List[List[int]] = []
        self.poi_to_group: dict[int: int] = {}

        self.last_fetch_success: bool = False
        self.current_region: Union[None, Region] = None
        self.available_fetched: bool = False
        self.divided: bool = False

        self.overpass = Overpass()
        self.nominatim = Nominatim()

        self.fetch_available_attraction_sets()

    def fetch_available_attraction_sets(self):
        collection = self.db_connection.get_collection_attractions("available_cities")

        available_regions_names = collection.find()

        for data in available_regions_names:
            self.available_regions.append(
                Region(data.get("city"), data.get("lat"), data.get("lon"), data.get("country")))

        self.available_country_region = list(map(lambda x: x.get_country_region().lower(), self.available_regions))
        self.available_region_names = list(map(lambda x: x.name.lower(), self.available_regions))
        self.available_fetched = True

    def fetch_pois(self, region_text="poland-kraków"):
        if not self.available_fetched:
            self.fetch_available_attraction_sets()

        region_text = region_text.lower()

        print(region_text, self.last_fetch_success, self.current_region is not None)
        if self.last_fetch_success and self.current_region is not None:
            if region_text == self.current_region.name.lower() or \
                    region_text == self.current_region.get_country_region().lower():
                return
            if region_text not in self.available_regions and region_text not in self.available_region_names:
                region = self.nominatim.query(region_text)

                region_data = region.toJSON()
                if len(region_data) == 0:
                    self.last_fetch_success = False
                    return
                if isinstance(region_data, list):
                    region_data = region_data[0]
                region_name = region_data.get("name")
                if region_name == self.current_region.name:
                    return

        if region_text in self.available_region_names:
            region_text = list(filter(lambda x: x.name.lower() == region_text, self.available_regions))[
                0].get_country_region()

        if region_text in self.available_country_region:
            collection = self.db_connection.get_collection_attractions(region_text)
            all_places = collection.find()

            self.pois = []
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
            self.current_region = list(filter(lambda x: x.get_country_region() == region_text, self.available_regions))[
                0]
            self.last_fetch_success = True
        else:
            self.fetch_attractions_from_osm(region_text)

    def fetch_attractions_from_osm(self, region_name):
        region = self.nominatim.query(region_name)

        region_data = region.toJSON()
        if len(region_data) == 0:
            self.last_fetch_success = False
            return
        if isinstance(region_data, list):
            region_data = region_data[0]

        region_name = region_data.get("name")
        self.current_region = Region(region_name, float(region_data.get("lat")), float(region_data.get("lon")))

        query_str = f'area["name"="{region_name}"]->.searchArea;('
        for selector in selectors:
            query_str += f'nwr["{selector[0]}"="{selector[1]}"](area.searchArea);'
        query_str += ');out body;>;out skel;'
        res = self.overpass.query(query_str)

        self.pois = []
        for element in res.toJSON().get('elements'):
            tags = element.get("tags")
            if tags is None:
                continue
            if tags.get("name") is None or element.get("type") is None or element.get("id") is None:
                continue

            lon = element.get("lon")
            lat = element.get("lat")
            if lon is None or lat is None:
                data = self.nominatim.query(f"{element.get('type')}/{element.get('id')}", lookup=True).toJSON()
                if isinstance(data, list):
                    if len(data) == 0:
                        continue
                    data = data[0]
                lon = data.get("lon")
                lat = data.get("lat")
                if lon is None or lat is None:
                    continue
            lon = float(lon)
            lat = float(lat)

            kinds = determine_kinds(tags)
            if len(kinds) == 0:
                continue
            kinds = []
            self.pois.append(
                PointOfInterest(name=tags.get('name'),
                                lon=lon,
                                lat=lat,
                                kinds=kinds,
                                xid=f"{element.get('type')[0].upper()}{element.get('id')}",
                                website=element.get('website'),
                                wiki=tags.get('wikipedia'),
                                opening_hours=tags.get('opening_hours')))

        self.last_fetch_success = True

    def get_places(self) -> List[PointOfInterest]:
        return self.pois

    def get_available_attraction_sets(self) -> List[Tuple[str, str]]:
        if not self.available_fetched:
            self.fetch_available_attraction_sets()
        return list(map(lambda x: (x.country, x.name), self.available_regions))

    def get_current_region(self) -> Region:
        if self.current_region is None:
            Region('', 50.0, 20.0, '')
        return self.current_region

    def get_current_region_name(self) -> str:
        if self.current_region is None:
            return ''
        return self.current_region.name


if __name__ == "__main__":
    print("a" == 'a')

"""
overpass = Overpass()
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
                
                 def divide_places(self):
        if self.divided:
            return
        if not self.last_fetch_success:
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
        
            def get_groups(self):
        if not self.last_fetch_success:
            self.fetch_pois()
        if not self.divided:
            self.divide_places()
        return self.groups

    def get_poi_to_group_mapping(self):
        if not self.last_fetch_success:
            self.fetch_pois()
        if not self.divided:
            self.divide_places()
        return self.poi_to_group
"""
