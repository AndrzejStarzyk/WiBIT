from typing import List, Tuple

from numpy import inf

from recommending_v2.categories.estimated_visiting import VisitingTimeProvider
from recommending_v2.model.point_of_interest import PointOfInterest
from recommending_v2.model.schedule import Day
from recommending_v2.model.user import User
from recommending_v2.poi_provider import PoiProvider


class Evaluator:
    def __init__(self, user: User):
        self.user = user
        self.places_provider: PoiProvider = PoiProvider()
        self.places: List[PointOfInterest] = self.places_provider.get_places()
        self.groups = self.places_provider.get_groups()
        self.poi_to_group = self.places_provider.get_poi_to_group_mapping()
        self.already_recommended: List[bool] = [False for _ in range(len(self.places))]

        self.visiting_time_provider = VisitingTimeProvider()

    def evaluate(self, day: Day, group_id: int) -> List[Tuple[int, float]]:
        self.user.decay_weights()
        evaluated_places: List[Tuple[int, float]] = [(i, self.user.evaluate(self.places[i])) for i in
                                                     range(len(self.places))
                                                     if not self.already_recommended[i] and
                                                     self.places[i].opening_hours.is_open(day.weekday, day.start.time(),
                                                                                          day.end.time()) and
                                                     self.poi_to_group[i] == group_id]
        evaluated_places.sort(key=lambda x: x[1], reverse=True)
        return evaluated_places

    def extract_best_trajectory(self, day: Day) -> List[Tuple[PointOfInterest, float]]:
        best_score = -inf
        best_list: List[Tuple[int, float]] = []
        for group in self.groups:
            place_id_score: List[Tuple[int, float]] = self.evaluate(day, group)
            score: float = 0.0
            i = 0
            curr_time = day.start
            while i < len(place_id_score) and curr_time < day.end:
                score += place_id_score[i][1]
                curr_time += self.visiting_time_provider.get_visiting_time(self.places[place_id_score[i][0]])
                i += 1

            if score > best_score:
                best_list = [place_id_score[j] for j in range(i)]

        for idx, _ in best_list:
            self.already_recommended[idx] = True

        return [(self.places[id_score[0]], id_score[1]) for id_score in best_list]


if __name__ == "__main__":
    pass
