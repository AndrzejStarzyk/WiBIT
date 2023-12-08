from enum import Enum
from typing import List, Tuple

from recommending_v2.point_of_interest.point_of_interest import PointOfInterest
from recommending_v2.categories.categories_provider import CategoriesProvider
from recommending_v2.utils import dist


class ConstraintType(Enum):
    Category = "category"
    Attraction = "attraction"
    Proximity = "proximity"


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

    def evaluate(self, poi: PointOfInterest) -> float:
        if poi.xid in self.xid_list:
            if self.is_wanted:
                return 1.0
            else:
                return -1.0
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

    def evaluate(self, pois_scores: List[Tuple[PointOfInterest, float]]) -> List[Tuple[PointOfInterest, float]]:
        pass

    def modify(self):
        pass

    def get_weight(self) -> int:
        pass

    def get_decay(self) -> int:
        return 1

    def to_json(self):
        return {}


class ProximityConstraint(GeneralConstraint):
    def __init__(self, best_pois_nr=3, radius=500, rate=0.8):
        super().__init__()
        self.best_pois_nr = best_pois_nr
        self.radius = radius
        self.rate = rate

        self.weight = 1

        self.modifications = [500, 1000, 250, 2000]

    def evaluate(self, pois_scores: List[Tuple[PointOfInterest, float]]) -> List[Tuple[PointOfInterest, float]]:
        for i in range(min(self.best_pois_nr, len(pois_scores))):
            poi, score = pois_scores[i]
            for j in range(i + 1, len(pois_scores)):
                poi_other, score_other = pois_scores[j]
                if dist(poi, poi_other) < self.radius:
                    pois_scores[j] = (poi_other, (1 - self.rate) * score_other + score * self.rate)
        return pois_scores

    def modify(self):
        curr = 0
        if self.radius in self.modifications:
            curr = self.modifications.index(self.radius)

        self.radius = self.modifications[(curr + 1) % len(self.modifications)]

    def get_weight(self) -> int:
        return self.weight

    def to_json(self):
        return {
            "constraint_type": ConstraintType.Attraction.value,
            "value": [self.best_pois_nr, self.radius, self.rate],
            "weight": self.weight
        }


if __name__ == '__main__':
    a = (1, 2)
