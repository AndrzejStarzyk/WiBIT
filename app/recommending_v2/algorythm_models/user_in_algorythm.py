from typing import List, Tuple

from recommending_v2.algorythm_models.constraint import Constraint, CategoryConstraint, GeneralConstraint
from recommending_v2.point_of_interest.point_of_interest import PointOfInterest


class Preference:
    def __init__(self, constraint: Constraint, weight: int):
        self.constraint: Constraint = constraint
        self.weight: int = weight


base_score = 0.1


class User:
    def __init__(self):
        self.preferences: List[Preference] = []
        self.total_weights: int = 0
        self.general_constraints: List[GeneralConstraint] = []
        self.permanent_preferences: List[Preference] = []

    def add_constraint(self, constraint: Constraint, weight: int):
        self.preferences.append(Preference(constraint, weight))
        self.total_weights += weight

    def add_permanent_preference(self, constraint: Constraint):
        self.permanent_preferences.append(Preference(constraint, constraint.get_weight()))

    def reset_permanent_preference(self):
        self.permanent_preferences = []

    def add_general_constraint(self, constraint: GeneralConstraint):
        self.general_constraints.append(constraint)

    def reset(self):
        self.preferences = []
        for preference in self.permanent_preferences:
            self.preferences.append(preference)

    def evaluate(self, poi: PointOfInterest) -> float:
        res = 0
        for pref in self.preferences:
            res += pref.constraint.evaluate(poi) * pref.weight

        if self.total_weights == 0:
            return base_score

        res /= self.total_weights
        res += base_score
        return res

    def decay_weights(self):
        for pref in self.preferences:
            decay = pref.constraint.get_decay()
            if pref.weight < decay:
                decay = pref.weight
            pref.weight = pref.weight - decay
            self.total_weights -= decay
        for pref in [i for i in self.preferences if i.weight <= 0]:
            self.preferences.remove(pref)

    def general_evaluation(self, pois_score: List[Tuple[PointOfInterest, float]]) -> List[Tuple[PointOfInterest, float]]:
        res = pois_score
        for constraint in self.general_constraints:
            res = constraint.evaluate(res)
        return res

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
