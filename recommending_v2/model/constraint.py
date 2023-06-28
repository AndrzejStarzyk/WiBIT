import string
from typing import List
from recommending_v2.model.point_of_interest import PointOfInterest

from reccomending_v1.opentripmaps_categories import CategoriesProvider


class Constraint:
    def __init__(self):
        pass

    def evaluate(self, poi: PointOfInterest):
        pass


class CategoryConstraint(Constraint):
    def __init__(self, codes: List[str]):
        super().__init__()
        self.codes: List[str] = codes
        self.provider: CategoriesProvider = CategoriesProvider()

    def evaluate(self, poi: PointOfInterest) -> int:
        return self.provider.get_score(poi.kinds, self.codes)


class AttractionConstraint(Constraint):
    def __init__(self, xid_list: List[str], is_wanted: bool = True):
        super().__init__()
        self.xid_list: List[str] = xid_list
        self.is_wanted: bool = is_wanted

    def evaluate(self, poi: PointOfInterest) -> int:
        if poi.xid in self.xid_list:
            if self.is_wanted:
                return 1
            else:
                return 0
        return 0
