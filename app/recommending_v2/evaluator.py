from typing import List, Tuple

from recommending_v2.categories.estimated_visiting import VisitingTimeProvider
from recommending_v2.point_of_interest.point_of_interest import PointOfInterest
from recommending_v2.algorythm_models.schedule import Day
from recommending_v2.algorythm_models.user_in_algorythm import User
from recommending_v2.point_of_interest.poi_provider import PoiProvider


class Evaluator:
    def __init__(self, user: User, poi_provider: PoiProvider, visiting_time_provider: VisitingTimeProvider):
        self.user = user
        self.places_provider: PoiProvider = poi_provider
        self.places: List[PointOfInterest] = []
        self.already_recommended: List[str] = []

        self.visiting_time_provider = visiting_time_provider

        self.evaluated_places: List[Tuple[PointOfInterest, float]] = []
        self.poi_evaluated = False

    def setup(self):
        print(self.places_provider.region_changed)
        if self.places_provider.region_changed:
            self.places = self.places_provider.get_places()
            print(len(self.places))
            self.places_provider.region_changed = False
        self.already_recommended = []
        self.evaluate()
        print(len(self.evaluated_places))

    def evaluate(self):
        self.evaluated_places: List[Tuple[PointOfInterest, float]] = [(i, self.user.evaluate(i)) for i in self.places]

        self.evaluated_places.sort(key=lambda x: x[1], reverse=True)
        self.user.decay_weights()
        self.poi_evaluated = True

    def extract_best_trajectory(self, day: Day) -> List[Tuple[PointOfInterest, float]]:
        place_id_score: List[Tuple[PointOfInterest, float]] = self.user.general_evaluation(self.evaluated_places)
        for poi, s in place_id_score:
            res = list(filter(lambda x: x[0].xid == poi.xid, self.evaluated_places))
            if len(res) > 0:
                print(poi.name, s, res[0][1])
        res = []
        i = 0
        curr_time = day.start
        while i < len(place_id_score) and curr_time < day.end:
            poi: PointOfInterest = place_id_score[i][0]
            if poi.opening_hours.is_open(day.weekday, day.start.time(),
                                         day.end.time()) and poi.xid not in self.already_recommended:
                curr_time += self.visiting_time_provider.get_visiting_time(poi)
                res.append((poi, place_id_score[i][1]))
            i += 1

        return res

    def add_already_recommended(self, xids: List[str]):
        for xid in xids:
            self.already_recommended.append(xid)


if __name__ == "__main__":
    a = {'a', 'b'}
    print(a)
