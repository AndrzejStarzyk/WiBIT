from typing import List

from creating_trip.algorythm_models.opening_hours import OpeningHours, parse_opening_hours


def placeholder_poi(xid: str = 'placeholder', name: str = 'placeholder', lon: float = 0, lat: float = 0,
                    website: str = '', wiki: str = '', opening_hours: str = ''):

    return PointOfInterest(xid, name, lon, lat, [], website, wiki, opening_hours)


class PointOfInterest:
    def __init__(self, xid: str, name: str, lon: float, lat: float, kinds: List[str],
                 website: str, wiki: str, opening_hours: str):
        self.xid: str = xid
        self.name: str = name
        self.lat: float = lat
        self.lon: float = lon
        self.kinds: List[str] = kinds
        self.website = website
        self.wiki = wiki
        self.opening_hours: OpeningHours = parse_opening_hours(opening_hours)

    def __str__(self):
        res = f"xid: {self.xid}, name: {self.name}, lat: {self.lat}, lon: {self.lon}, kinds: "
        for kind in self.kinds:
            res += kind + ", "
        return res[0:-2]
