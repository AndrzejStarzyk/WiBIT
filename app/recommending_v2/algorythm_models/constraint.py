from enum import Enum
from typing import List
from point_of_interest import PointOfInterest

from recommending_v2.categories.categories_provider import CategoriesProvider


class ConstraintType(Enum):
    Category = "category"
    Attraction = "attraction"


class Constraint:
    def __init__(self):
        pass

    def evaluate(self, poi: PointOfInterest) -> float:
        pass

    def get_weight(self) -> int:
        pass

    def get_decay(self) -> int:
        return 4

    def to_json(self):
        return {}


class CategoryConstraint(Constraint):
    def __init__(self, codes: List[str], db_connection):
        super().__init__()
        self.codes: List[str] = codes
        self.provider: CategoriesProvider = CategoriesProvider(db_connection)
        self.weight = 20

    def evaluate(self, poi: PointOfInterest) -> float:
        return self.provider.compute_score(self.codes, poi.kinds)

    def get_weight(self):
        return self.weight

    def __str__(self):
        res = "codes: "
        for code in self.codes:
            res += f"{code}, "
        return res[0:-2]

    def to_json(self):
        return {
            "constraint_type": ConstraintType.Category.value,
            "value": self.codes,
            "weight": self.weight
        }


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

    def get_weight(self):
        return self.weight

    def __str__(self):
        res = "xid list: "
        for xid in self.xid_list:
            res += f"{xid}, "
        return res[0:-2]

    def to_json(self):
        return {
            "constraint_type": ConstraintType.Attraction.value,
            "value": self.xid_list,
            "weight": self.weight
        }


class GeneralConstraint:
    def __init__(self):
        pass

    def evaluate(self, poi: List[PointOfInterest]):
        pass

    def get_weight(self) -> int:
        pass

    def get_decay(self) -> int:
        return 1

    def to_json(self):
        return {}


class ProximityConstraint(GeneralConstraint):
    pass


if __name__ == '__main__':
    print(ConstraintType.Category.value)
