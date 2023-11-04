from typing import List, Tuple

from categories.estimated_visiting import VisitingTimeProvider
from algorythm_models.point_of_interest import PointOfInterest
from algorythm_models.schedule import Day
from algorythm_models.user_in_algorythm import User
from poi_provider import PoiProvider


class Evaluator:
    def __init__(self, user: User, poi_provider: PoiProvider, visiting_time_provider: VisitingTimeProvider):
        self.user = user
        self.places_provider: PoiProvider = poi_provider
        self.places: List[PointOfInterest] = self.places_provider.get_places()
        # self.groups = self.places_provider.get_groups()
        # self.poi_to_group = self.places_provider.get_poi_to_group_mapping()
        self.already_recommended: List[str] = []

        self.visiting_time_provider = visiting_time_provider

        self.evaluated_places: List[Tuple[int, float]] = []
        self.poi_evaluated = False

    def evaluate(self):
        self.evaluated_places: List[Tuple[int, float]] = [(i, self.user.evaluate(self.places[i])) for i in range(len(self.places))]

        self.evaluated_places.sort(key=lambda x: x[1], reverse=True)
        print("---------------------------------------------------")
        for i, s in self.evaluated_places:
            print(self.places[i].name, s)
        self.user.decay_weights()
        self.poi_evaluated = True

    def extract_best_trajectory(self, day: Day) -> List[Tuple[PointOfInterest, float]]:
        place_id_score: List[Tuple[int, float]] = self.evaluated_places

        score: float = 0.0
        i = 0
        curr_time = day.start
        while i < len(place_id_score) and curr_time < day.end:
            poi: PointOfInterest = self.places[place_id_score[i][0]]
            if poi.opening_hours.is_open(day.weekday, day.start.time(), day.end.time()) and poi.xid not in self.already_recommended:
                score += place_id_score[i][1]
                curr_time += self.visiting_time_provider.get_visiting_time(poi)
            i += 1

        return [(self.places[place_id_score[j][0]], place_id_score[j][1]) for j in range(i)]

    def add_already_recommended(self, xids: List[str]):
        for xid in xids:
            self.already_recommended.append(xid)

    def setup(self):
        self.already_recommended = []
        self.evaluate()



if __name__ == "__main__":
    a = {'a', 'b'}
    print(a)
