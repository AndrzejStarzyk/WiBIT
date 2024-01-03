from math import sqrt, cos, pi
from datetime import datetime

from creating_trip.point_of_interest.point_of_interest import PointOfInterest

deg_to_m = 40075014 / 360  # m/deg
earth_radius = 6371009  # m
short_dist = 500  # m
walking_speed = 0.5  # m/s
driving_speed = 3.7  # m/s


def dist(poi1: PointOfInterest, poi2: PointOfInterest) -> float:  # m
    dlat = (poi1.lat - poi2.lat) * pi / 180
    dlon = (poi1.lon - poi2.lon) * pi / 180
    mlat = (poi1.lat + poi2.lat) / 2 * pi / 180
    return earth_radius * sqrt(pow(dlat, 2) + pow(cos(mlat) * dlon, 2))


def estimated_time(s) -> float:  # m -> s
    if s < short_dist:
        return s / walking_speed
    else:
        return s / driving_speed


def round_time(time: datetime):
    return datetime(time.year, time.month, time.day, time.hour, time.minute - (time.minute % 5), 0, 0)
