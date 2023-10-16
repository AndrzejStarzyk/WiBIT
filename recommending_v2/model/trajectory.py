from datetime import time
from typing import List, Tuple

from recommending_v2.model.point_of_interest import PointOfInterest


class Trajectory:
    def __init__(self, pois: List[PointOfInterest] = None):
        if pois is None:
            pois = []
        self.pois: List[PointOfInterest] = pois
        self.extra_info: List[Tuple[str, time, time]] = []

    def add_poi(self, poi: PointOfInterest):
        self.pois.append(poi)


