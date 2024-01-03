from typing import List, Tuple, Union

from creating_trip.categories.estimated_visiting import VisitingTimeProvider
from creating_trip.evaluator import Evaluator
from creating_trip.poi_provider import PoiProvider
from creating_trip.trajectory_builder import build_trajectory
from creating_trip.algorythm_models.user_in_algorythm import User
from creating_trip.algorythm_models.constraint import Constraint, ProximityConstraint, ConstraintType
from creating_trip.algorythm_models.trajectory import Trajectory
from creating_trip.algorythm_models.schedule import Schedule


class Recommender:
    def __init__(self, user: User, poi_provider: PoiProvider, visiting_time_provider: VisitingTimeProvider):
        self.user: User = user
        self.visiting_time_provider = visiting_time_provider
        self.evaluator: Evaluator = Evaluator(self.user, poi_provider, visiting_time_provider)

        self.cold_start: bool = True

        self.dates: List[str] = []
        self.days: int = 0
        self.hours: List[Tuple[str, str]] = []
        self.schedule: Union[Schedule, None] = None

        self.logged_user_preferences_fetched = False

    def set_user(self, user: User):
        self.user = user

    def add_constraint(self, constraint: Constraint):
        if self.cold_start and constraint.to_json()["constraint_type"] == ConstraintType.Category.value:
            self.cold_start = False
        self.user.add_constraint(constraint, constraint.get_weight())

    def modify_general_constraint(self):
        if len(self.user.general_constraints) == 0:
            self.user.add_general_constraint(ProximityConstraint())
        else:
            self.user.general_constraints[0].modify()

    def create_schedule(self):
        self.schedule = Schedule(self.days, self.dates, self.hours)

    def get_recommended(self) -> Schedule:
        self.create_schedule()

        if self.cold_start:
            self.user.add_general_constraint(ProximityConstraint(best_pois_nr=1))
        self.evaluator.setup(self.cold_start)
        for day in self.schedule.schedule:
            best_pois = self.evaluator.extract_best_trajectory(day)
            trajectory: Trajectory = build_trajectory(day, best_pois, self.visiting_time_provider)
            self.evaluator.add_already_recommended(list(map(lambda x: x.poi.xid, trajectory.get_events())))
            self.schedule.add_trajectory(trajectory)
        return self.schedule

    def recommend_again(self, day_id: int) -> Schedule:
        if self.cold_start:
            self.cold_start = False
            return self.get_recommended()
        if day_id < 0 or day_id >= len(self.schedule.schedule):
            return self.schedule
        self.evaluator.evaluate(cold_start=False)
        best_pois = self.evaluator.extract_best_trajectory(self.schedule.schedule[day_id])
        trajectory: Trajectory = build_trajectory(self.schedule.schedule[day_id], best_pois,
                                                  self.visiting_time_provider)
        self.schedule.replace_trajectory(trajectory, day_id)
        return self.schedule

    def remove_from_schedule(self, day_id, xids: List[str]) -> Schedule:
        if day_id < 0 or day_id >= len(self.schedule.schedule):
            return self.schedule
        to_remove = []
        trajectory = self.schedule.trajectories[day_id]
        for xid in xids:
            for event in trajectory.events:
                if event.poi.xid == xid:
                    to_remove.append(event)

        for i in to_remove:
            trajectory.events.remove(i)

        return self.schedule
