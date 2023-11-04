from typing import List, Tuple, Union

from estimated_visiting import VisitingTimeProvider
from evaluator import Evaluator
from poi_provider import PoiProvider
from trajectory_builder import build_trajectory
from algorythm_models.user_in_algorythm import User
from algorythm_models.default_trip import DefaultTrip
from algorythm_models.constraint import Constraint
from algorythm_models.trajectory import Trajectory
from algorythm_models.schedule import Schedule


class Recommender:
    def __init__(self, user: User, poi_provider: PoiProvider, visiting_time_provider: VisitingTimeProvider,
                 default_trip: DefaultTrip):
        self.user: User = user
        self.visiting_time_provider = visiting_time_provider
        self.default_trip = default_trip
        self.evaluator: Evaluator = Evaluator(self.user, poi_provider, visiting_time_provider)
        self.cold_start: bool = True
        self.pois_limit: int = 100
        self.dates: List[str] = []
        self.days: int = 0
        self.hours: List[Tuple[str, str]] = []
        self.schedule: Union[Schedule, None] = None

    def set_user(self, user: User):
        self.user = user
        self.cold_start = False

    def add_constraint(self, constraint: Constraint):
        if self.cold_start:
            self.cold_start = False
        self.user.add_constraint(constraint, constraint.get_weight())

    def create_schedule(self):
        self.schedule = Schedule(self.days, self.dates, self.hours)

    def get_recommended(self) -> Schedule:
        if self.cold_start:
            trip = self.default_trip.get_trip(self.schedule.schedule[0])
            self.schedule.add_trajectory(trip)
            return self.schedule
        else:
            print(self.user)
            self.evaluator.setup()
            for day in self.schedule.schedule:
                best_pois = self.evaluator.extract_best_trajectory(day)
                print("--------------------------------------------------------")
                for i, s in best_pois:
                    print(i.name, s)
                trajectory: Trajectory = build_trajectory(day, best_pois, self.visiting_time_provider)
                self.evaluator.add_already_recommended(list(map(lambda x: x.poi.xid, trajectory.get_events())))
                self.schedule.add_trajectory(trajectory)

            return self.schedule


if __name__ == "__main__":
    a = [0, 1, 2]
    print(a[0:0])

"""

def get_estimated_visiting_time(kinds: List[str]):
    time = timedelta()
    total = 0
    for i in categories:
        if i.get('code') in kinds:
            time += i.get('visiting_time')
    if total == 0:
        return time

    return time / total
    
    def fill_schedule(self, idxs: List[int]):
        trajectory = Trajectory([self.places[idx] for idx in idxs[0:self.pois_limit]])
        best_path: List[Tuple[PointOfInterest, bool]] = [(i, False) for i in pretty_path(trajectory)]

        for day in self.schedule.schedule:
            current: datetime = day.start
            prev_coords: Union[Tuple[float, float], None] = None
            for i in range(len(best_path)):
                poi = best_path[i][0]
                taken = best_path[i][1]
                if taken:
                    continue
                visiting_time = get_estimated_visiting_time(poi.kinds)
                travel_time = timedelta()
                if prev_coords is not None:
                    dist = math.sqrt((prev_coords[0] - poi.lon) * (prev_coords[0] - poi.lon) +
                                     (prev_coords[1] - poi.lat) * (prev_coords[1] - poi.lat)) * deg_to_m
                    if dist < short_dist:
                        if dist * walking_speed < 3600 * 24:
                            travel_time = timedelta(seconds=dist / walking_speed)
                        else:
                            continue
                    else:
                        if dist * walking_speed < 3600 * 24:
                            travel_time = timedelta(seconds=dist / driving_speed)
                        else:
                            continue

                visit_start = current + travel_time
                later = visit_start + visiting_time
                if later < day.end and poi.opening_hours.is_open(day.weekday, visit_start.time(), later.time()):
                    day.add_event(visit_start.time(), later.time(), poi)
                    current = later
                    prev_coords = (poi.lon, poi.lat)
                    best_path[i] = (poi, True)
                else:
                    continue

    def trajectory_from_schedule(self) -> Trajectory:
        pois = []
        extra = []
        for day in self.schedule.schedule:
            for event in day.events:
                pois.append(event.poi)
                extra.append((day.date_str, event.start.isoformat(), event.end.isoformat()))

        trajectory = Trajectory(pois)
        trajectory.extra_info = extra
        return trajectory

    def set_pois_limit(self, number: int):
        self.pois_limit = min(number, 15)


def pretty_path(trajectory: Trajectory) -> List[PointOfInterest]:
    dl = len(trajectory.pois)
    if dl < 2:
        return trajectory.pois
    graph = [[math.sqrt((coordinates1.lon - coordinates2.lon) * (coordinates1.lon - coordinates2.lon) +
                        (coordinates1.lat - coordinates2.lat) * (coordinates1.lat - coordinates2.lat))
              for coordinates2 in trajectory.pois] for coordinates1 in trajectory.pois]

    shortest_paths: List[List[Tuple[float, int]]] = [[(0, -1) for _ in range(0, dl - 1)] for _ in
                                                     range(0, 2 ** (dl - 1))]
    max_sum = sum([sum(graph[i]) for i in range(0, dl)])
    for i in range(0, dl - 1):
        shortest_paths[0][i] = (graph[dl - 1][i], 0)

    def number_to_permutation(n_: int) -> List[int]:
        res_: List[int] = []
        for i_ in range(0, dl - 1):
            if n_ % 2 == 1:
                res_.append(i_)
            n_ = n_ // 2
        return res_

    def compute(row_, col_):

        perm = number_to_permutation(row_)

        shortest_ = max_sum
        pre_last_ = -1
        for i_ in perm:
            if shortest_paths[row_ - 2 ** i_][i_][1] == -1:
                compute(row_ - 2 ** i_, i_)
            if shortest_paths[row_ - 2 ** i_][i_][0] + graph[i_][col_] < shortest_:
                shortest_ = shortest_paths[row_ - 2 ** i_][i_][0] + graph[i_][col_]
                pre_last_ = i_
        shortest_paths[row_][col_] = (shortest_, pre_last_)

    shortest = max_sum
    last = -1
    for col in range(0, dl - 1):
        row = 2 ** (dl - 1) - 1 - 2 ** col
        if shortest_paths[row][col][1] == -1:
            compute(row, col)
        if shortest_paths[row][col][0] < shortest:
            shortest = shortest_paths[row][col][0]
            last = col

    path = []
    row = 2 ** (dl - 1) - 1 - 2 ** last
    for i in range(0, dl - 1):
        path.append(last)
        last = shortest_paths[row][last][1]
        row -= 2 ** last
    path.append(dl - 1)

    longest = graph[path[0]][path[dl - 1]]
    first = 0
    for i in range(0, dl - 1):
        if graph[path[i]][path[i + 1]] > longest:
            longest = graph[path[i]][path[i + 1]]
            first = i

    res = []
    for i in range(first, dl):
        res.append(path[i])
    for i in range(0, first):
        res.append(path[i])

    return [trajectory.pois[i] for i in res]

"""
