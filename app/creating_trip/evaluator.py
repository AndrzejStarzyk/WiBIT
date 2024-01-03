from typing import List, Tuple

from creating_trip.categories.estimated_visiting import VisitingTimeProvider
from creating_trip.point_of_interest.point_of_interest import PointOfInterest, placeholder_poi
from creating_trip.algorythm_models.schedule import Day
from creating_trip.algorythm_models.user_in_algorythm import User
from creating_trip.poi_provider import PoiProvider


class Evaluator:
    def __init__(self, user: User, poi_provider: PoiProvider, visiting_time_provider: VisitingTimeProvider):
        self.user = user
        self.places_provider: PoiProvider = poi_provider
        self.current_region_name: str = ''

        self.places: List[PointOfInterest] = []
        self.already_recommended: List[str] = []

        self.visiting_time_provider = visiting_time_provider

        self.evaluated_places: List[Tuple[PointOfInterest, float]] = []
        self.poi_evaluated = False

        self.placeholder_to_remove = False
        self.placeholder: PointOfInterest = placeholder_poi()

    def setup(self, cold_start: bool):
        if self.places_provider.get_current_region_name() != self.current_region_name:
            self.places = self.places_provider.get_places()
            self.current_region_name = self.places_provider.get_current_region_name()

        self.placeholder_to_remove = False
        if cold_start:
            self.placeholder.lat = self.places_provider.get_current_region().lat
            self.placeholder.lon = self.places_provider.get_current_region().lon

        self.already_recommended = []
        self.evaluate(cold_start)

    def evaluate(self, cold_start):
        self.evaluated_places: List[Tuple[PointOfInterest, float]] = [(i, self.user.evaluate(i)) for i in self.places]
        self.evaluated_places.sort(key=lambda x: x[1], reverse=True)

        if cold_start:
            self.places.append(self.placeholder)
            max_score = self.evaluated_places[0][1]
            self.evaluated_places.insert(0, (self.placeholder, max_score+2))
            self.placeholder_to_remove = True

        self.user.decay_weights()
        self.poi_evaluated = True

    def extract_best_trajectory(self, day: Day) -> List[Tuple[PointOfInterest, float]]:
        poi_score: List[Tuple[PointOfInterest, float]] = self.user.general_evaluation(self.evaluated_places)

        if self.placeholder_to_remove:
            to_remove = list(filter(lambda x: x[0].xid == 'placeholder', poi_score))
            if len(to_remove) > 0:
                poi_score.remove(to_remove[0])
                self.places.remove(self.placeholder)

        res = []
        i = 0
        curr_time = day.start
        while i < len(poi_score) and curr_time < day.end:
            poi: PointOfInterest = poi_score[i][0]
            if poi.opening_hours.is_open(day.weekday, day.start.time(),
                                         day.end.time()) and poi.xid not in self.already_recommended:
                curr_time += self.visiting_time_provider.get_visiting_time(poi)
                res.append((poi, poi_score[i][1]))
            i += 1

        return res

    def add_already_recommended(self, xids: List[str]):
        for xid in xids:
            self.already_recommended.append(xid)
