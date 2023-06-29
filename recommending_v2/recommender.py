from typing import List

from recommending_v2.poi_provider import Provider
from recommending_v2.model.user import User
from recommending_v2.model.default_trip import DefaultTrip
from recommending_v2.model.constraint import Constraint
from recommending_v2.model.point_of_interest import PointOfInterest
from recommending_v2.model.trajectory import Trajectory


class Recommender:
    def __init__(self):
        self.places_provider: Provider = Provider()
        self.places: List[PointOfInterest] = self.places_provider.get_places()
        self.user = User()
        self.cold_start = True
        self.pois_limit = 0

    def set_user(self, user: User):
        self.user = user
        self.cold_start = False

    def add_constraint(self, constraint: Constraint, weight: int = 5):
        if self.cold_start:
            self.cold_start = False
        self.user.add_constraint(constraint, weight)

    def get_recommended(self) -> Trajectory:
        if self.cold_start:
            trip = DefaultTrip()
            return trip.get_trip()
        else:
            evaluated_places = [(i, self.user.evaluate(self.places[i])) for i in range(len(self.places))]
            evaluated_places.sort(key=lambda x: x[1])

            return self.trip_from_pois_id([i[0] for i in evaluated_places])

    def trip_from_pois_id(self, pois: List[int]) -> Trajectory:
        print(self.pois_limit)
        trajectory = Trajectory()
        for id in pois[0:self.pois_limit]:
            trajectory.add_poi(self.places[id])
        return trajectory

    def set_pois_limit(self, number: int):
        self.pois_limit = number

