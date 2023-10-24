from typing import List, TypedDict

from recommending_v2.model.constraint import Constraint, AttractionConstraint
from recommending_v2.model.point_of_interest import PointOfInterest
from recommending_v2.model.default_trip import get_default_places_xid


class Preference(TypedDict):
    constraint: Constraint
    weight: int


base_score = 0.1


class User:
    def __init__(self):
        self.preferences: List[Preference] = []
        self.total_weights: int = 0

        for xid in get_default_places_xid():
            self.add_constraint(AttractionConstraint([xid]), 15)

    def add_constraint(self, constraint: Constraint, weight: int):
        self.preferences.append({'constraint': constraint, 'weight': weight})
        self.total_weights += weight

    def evaluate(self, poi: PointOfInterest) -> float:
        res = base_score
        for pref in self.preferences:
            res += pref['constraint'].evaluate(poi) * pref['weight']
        if self.total_weights != 0:
            res /= self.total_weights

        return res

    def decay_weights(self):   # TODO: check if decaying weights can drop below 0
        for pref in self.preferences:
            decay = pref['constraint'].get_decay()
            pref['weight'] = pref['weight'] - decay
            self.total_weights -= decay
        for pref in [i for i in self.preferences if i['weight'] <= 0]:
            self.preferences.remove(pref)

    def save_state(self):
        pass
