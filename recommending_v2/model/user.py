from recommending_v2.model.constraint import Constraint
from recommending_v2.model.point_of_interest import PointOfInterest


class User:
    def __init__(self):
        self.preferences = []
        self.total_weights = 0

    def add_constraint(self, constraint: Constraint, weight: int):
        self.preferences.append((constraint, weight))
        self.total_weights += weight

    def evaluate(self, poi: PointOfInterest):
        res = 0
        for constraint, weight in self.preferences:
            res += constraint.evaluate(poi) * weight

        if self.total_weights != 0:
            res /= self.total_weights

        return res
