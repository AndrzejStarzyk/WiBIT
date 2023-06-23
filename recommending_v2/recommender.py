from typing import List

from recommending_v2.poi_provider import Provider
from recommending_v2.user import User
from recommending_v2.default_trip import DefaultTrip
from constraint import Constraint
from point_of_interest import PointOfInterest


class Recommender:
    def __init__(self):
        self.places_provider: Provider = Provider()
        self.places: List[PointOfInterest] = self.places_provider.get_places()
        self.user = User()
        self.cold_start = True

    def set_user(self, user: User):
        self.user = user
        self.cold_start = False

    def add_constraint(self, constraint: Constraint, weight: int):
        self.user.add_constraint(constraint, weight)

    def get_recommended(self):
        if self.cold_start:
            trip = DefaultTrip()
            return trip.get_trip()
        else:
            evaluated_places = [(i, self.user.evaluate(self.places[i])) for i in range(len(self.places))]
            evaluated_places.sort(key=lambda x: x[1])

            return self.trip_from_pois_id([i[0] for i in evaluated_places], 7)

    def trip_from_pois_id(self, pois: List[int], limit: int):
        return [(self.places[id].lon, self.places[id].lat, self.places[id].name) for id in pois[0:limit]]


