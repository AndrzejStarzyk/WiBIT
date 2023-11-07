from typing import List

from recommending_v2.algorythm_models.constraint import Constraint, AttractionConstraint, CategoryConstraint
from recommending_v2.algorythm_models.point_of_interest import PointOfInterest
from recommending_v2.algorythm_models.default_trip import get_default_places_xid


class Preference:
    def __init__(self, constraint: Constraint, weight: int):
        self.constraint: Constraint = constraint
        self.weight: int = weight


base_score = 0.1


class User:
    def __init__(self):
        self.preferences: List[Preference] = []
        self.total_weights: int = 0

        for xid in get_default_places_xid():
            self.add_constraint(AttractionConstraint([xid]), 3)

    def add_constraint(self, constraint: Constraint, weight: int):
        self.preferences.append(Preference(constraint, weight))
        self.total_weights += weight

    def evaluate(self, poi: PointOfInterest) -> float:
        res = 0
        for pref in self.preferences:
            res += pref.constraint.evaluate(poi) * pref.weight
        res /= self.total_weights
        res += base_score
        return res

    def decay_weights(self):  # TODO: check if decaying weights can drop below 0
        for pref in self.preferences:
            decay = pref.constraint.get_decay()
            pref.weight = pref.weight - decay
            self.total_weights -= decay
        for pref in [i for i in self.preferences if i.weight <= 0]:
            self.preferences.remove(pref)

    def get_category_preferences(self):
        res = []
        for pref in self.preferences:
            if isinstance(pref.constraint, CategoryConstraint):
                for code in pref.constraint.codes:
                    res.append(code)
        return res

    def __str__(self):
        res = ""
        for pref in self.preferences:
            res += f"{pref.constraint.__str__()}, {pref.weight}\n"
        return res
