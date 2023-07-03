import string
from typing import List
from recommending_v2.model.point_of_interest import PointOfInterest

from reccomending_v1.opentripmaps_categories import CategoriesProvider


class Constraint:
    def __init__(self):
        pass

    def evaluate(self, poi: PointOfInterest):
        pass

    def get_weight(self) -> int:
        pass

    def get_decay(self) -> int:
        return 1


class TripConstraint:
    def __init__(self):
        pass

    def evaluate(self, poi: PointOfInterest):
        pass


class CategoryConstraint(Constraint):
    def __init__(self, codes: List[str]):
        super().__init__()
        self.codes: List[str] = codes
        self.provider: CategoriesProvider = CategoriesProvider()
        self.weight = 20

    def evaluate(self, poi: PointOfInterest) -> int:
        return self.provider.get_score(poi.kinds, self.codes)

    def get_weight(self):
        return self.weight


class AttractionConstraint(Constraint):
    def __init__(self, xid_list: List[str], is_wanted: bool = True):
        super().__init__()
        self.xid_list: List[str] = xid_list
        self.is_wanted: bool = is_wanted
        self.weight = 100

    def evaluate(self, poi: PointOfInterest) -> int:

        if poi.xid in self.xid_list:
            if self.is_wanted:
                return 1
            else:
                return -1
        return 0

    def __str__(self):
        res = "xid list: "
        for xid in self.xid_list:
            res += f"xid:{xid}, "
        return res[0:-2]

    def get_weight(self):
        return self.weight


class TimeConstraint(TripConstraint):
    def __init__(self, datetime):
        super().__init__()
        print(datetime)
