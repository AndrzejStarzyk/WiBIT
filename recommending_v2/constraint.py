import string
from typing import List
from point_of_interest import PointOfInterest

from reccomending_v1.opentripmaps_categories import CategoriesProvider


class Constraint:
    def __init__(self):
        pass

    def evaluate(self, poi: PointOfInterest):
        pass


class CategoryConstraint(Constraint):
    def __init__(self, codes: List[string]):
        super().__init__()
        self.codes = codes
        self.provider = CategoriesProvider()

    def evaluate(self, poi: PointOfInterest):
        return self.provider.get_score(poi.kinds, self.codes)
