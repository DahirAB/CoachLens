from ortools.sat.python import cp_model
from typing import List, Dict, Tuple

from .data import EXERCISES, Exercise
from ..models.schemas import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    TrainingGoal,
    Weekday,
    ExercisePlan,
    IntensityLevel,
    WeightRangeKg,
    MuscleGroup,
)

class InfeasiblePlanError(Exception):
    pass


WEEKDAY_ORDER: Dict[Weekday, int] = {
    Weekday.MONDAY: 0,
    Weekday.TUESDAY: 1,
    Weekday.WEDNESDAY: 2,
    Weekday.THURSDAY: 3,
    Weekday.FRIDAY: 4,
    Weekday.SATURDAY: 5,
    Weekday.SUNDAY: 6,
}

# default params todo get from req 
DEFAULT_INTENSITY = IntensityLevel.MEDIUM
DEFAULT_REP_RANGE = "6-10"
DEFAULT_1RM_PERCENT_RANGE: Tuple[float, float] = (0.65, 0.80)

CARDIO_GROUP = MuscleGroup.CARDIO


class TrainingPlanOptimiser:
    def __init__(self, request: GeneratePlanRequest):
        self.request = request
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        
        self.available_exercises: List[Exercise] = [
            ex for ex in EXERCISES if ex.equipment in self.request.equipment
        ]

        
        self.days: List[Weekday] = sorted(
            self.request.available_days, key=lambda d: WEEKDAY_ORDER[d]
        )

    def solve(self) -> GeneratePlanResponse:
        
        x: Dict[Tuple[Weekday, int], cp_model.IntVar] = {}
        for day in self.days:
            for i in range(len(self.available_exercises)):
                x[(day, i)] = self.model.NewBoolVar(f"x_{day}_{i}")

        # constraint cant exceed session time 
        for day in self.days:
            self.model.Add(
                sum(
                    x[(day, i)] * self.available_exercises[i].duration_minutes
                    for i in range(len(self.available_exercises))
                )
                <= self.request.session_duration_minutes
            )

        # constraint each day has at least one exercise
        for day in self.days:
            self.model.Add(
                sum(x[(day, i)] for i in range(len(self.available_exercises))) >= 1
            )

        # constraint: limit how many exercises hit the same muscle on one day
        # prevents the solver spamming one muscle group to maximise the objective
        per_muscle_cap = 2
        for day in self.days:
            for mg in MuscleGroup:
                if mg == CARDIO_GROUP:
                    continue
                idxs = [i for i, ex in enumerate(self.available_exercises) if ex.muscle_group == mg]
                if idxs:
                    self.model.Add(sum(x[(day, i)] for i in idxs) <= per_muscle_cap)

        # constraint: avoid training the same muscle on back-to-back days
        # introduces basic recovery without fatigue modelling
        muscle_used: Dict[Tuple[Weekday, MuscleGroup], cp_model.IntVar] = {}
        for day in self.days:
            for mg in MuscleGroup:
                if mg == CARDIO_GROUP:
                    continue
                idxs = [i for i, ex in enumerate(self.available_exercises) if ex.muscle_group == mg]
                if not idxs:
                    continue
                y = self.model.NewBoolVar(f"muscle_{day}_{mg}")
                muscle_used[(day, mg)] = y
                # y == 0 -> sum == 0
                self.model.Add(sum(x[(day, i)] for i in idxs) == 0).OnlyEnforceIf(y.Not())
                # y == 1 -> sum >= 1
                self.model.Add(sum(x[(day, i)] for i in idxs) >= 1).OnlyEnforceIf(y)

        day_set = set(self.days)
        for day in self.days:
            next_order = WEEKDAY_ORDER[day] + 1
            next_day = next((d for d, o in WEEKDAY_ORDER.items() if o == next_order), None)
            if next_day is None or next_day not in day_set:
                continue
            for mg in MuscleGroup:
                if mg == CARDIO_GROUP:
                    continue
                y1 = muscle_used.get((day, mg))
                y2 = muscle_used.get((next_day, mg))
                if y1 is not None and y2 is not None:
                    self.model.Add(y1 + y2 <= 1)

        # objective: bias exercise selection based on training goal
        # keeps this as a soft preference (not a hard requirement)
        def _exercise_weight(ex: Exercise) -> int:
            if self.request.training_goal == TrainingGoal.STRENGTH:
                return 3 if ex.is_compound else 1
            if self.request.training_goal == TrainingGoal.FAT_LOSS:
                return 3 if ex.muscle_group == CARDIO_GROUP else 1
            if self.request.training_goal == TrainingGoal.HYPERTROPHY:
                # slight bias toward more total volume (shorter/non-compound accessories often allow more total work)
                return 2 if not ex.is_compound else 1
            return 1

        self.model.Maximize(
            sum(
                x[(day, i)] * _exercise_weight(self.available_exercises[i])
                for day in self.days
                for i in range(len(self.available_exercises))
            )
        )

        status = self.solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise InfeasiblePlanError("Unable to generate a feasible training plan.")

        # solver -> week_plan
        week_plan: Dict[Weekday, List[ExercisePlan]] = {}
        for day in self.days:
            exercises_for_day: List[ExercisePlan] = []
            for i, ex in enumerate(self.available_exercises):
                if self.solver.Value(x[(day, i)]):
                    exercises_for_day.append(self._format_exercise(ex))
            week_plan[day] = exercises_for_day

        return GeneratePlanResponse(
            training_goal=self.request.training_goal,
            deload_week=False,
            week_plan=week_plan,
            fatigue_summary=self.request.fatigue_levels,
        )

    def _format_exercise(self, ex: Exercise) -> ExercisePlan:
        # default intensity is medium todo add fatigue level logic
        intensity = DEFAULT_INTENSITY

        # get a weight range based on the 1RM todo get 1rm from req 
        weight_range = None
        if ex.primary_1rm_link:
            one_rm_value = getattr(self.request.one_rep_maxes, ex.primary_1rm_link)
            low_pct, high_pct = DEFAULT_1RM_PERCENT_RANGE

            min_weight = one_rm_value * low_pct * ex.weight_multiplier
            max_weight = one_rm_value * high_pct * ex.weight_multiplier

            weight_range = WeightRangeKg(
                min=float(round(min_weight)),
                max=float(round(max_weight)),
            )

        return ExercisePlan(
            name=ex.name,
            muscle_group=ex.muscle_group,
            equipment=ex.equipment,
            intensity_level=intensity,
            rep_range=DEFAULT_REP_RANGE,
            weight_range_kg=weight_range,
        )
