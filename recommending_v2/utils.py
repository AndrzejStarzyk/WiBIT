from math import sqrt

from recommending_v2.model.point_of_interest import PointOfInterest

deg_to_m = 40075014 / 360  # m/deg
short_dist = 500  # m
walking_speed = 0.5  # m/s
driving_speed = 4  # m/s


def dist(poi1: PointOfInterest, poi2: PointOfInterest) -> float:  # m
    return sqrt(
        (poi1.lat - poi2.lat) * (poi1.lat - poi2.lat) + (poi1.lon - poi2.lon) * (poi1.lon - poi2.lon)) * deg_to_m


def estimated_time(s) -> float:  # m -> s
    if s < short_dist:
        return s / walking_speed
    else:
        return s / driving_speed
