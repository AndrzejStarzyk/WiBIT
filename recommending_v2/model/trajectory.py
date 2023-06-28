from typing import List

from recommending_v2.model.point_of_interest import PointOfInterest


class Trajectory:
    def __init__(self, pois: List[PointOfInterest] = None):
        if pois is None:
            pois = []
        self.pois: List[PointOfInterest] = pois

    def add_poi(self, poi: PointOfInterest):
        self.pois.append(poi)


