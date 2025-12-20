from ortools.sat.python import cp_model
from typing import List, Dict, Tuple

from .data import EXERCISES, Exercise
from ..models.schemas import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    Weekday,
    ExercisePlan,
    IntensityLevel,
    WeightRangeKg,
)

class InfeasiblePlanError(Exception):
    pass


# Used to keep weekday ordering consistent (Mon → Sun)
WEEKDAY_ORDER: Dict[Weekday, int] = {
    Weekday.MONDAY: 0,
    Weekday.TUESDAY: 1,
    Weekday.WEDNESDAY: 2,
    Weekday.THURSDAY: 3,
    Weekday.FRIDAY: 4,
    Weekday.SATURDAY: 5,
    Weekday.SUNDAY: 6,
}

# Fixed training parameters for the basic engine
DEFAULT_INTENSITY = IntensityLevel.MEDIUM
DEFAULT_REP_RANGE = "6-10"
DEFAULT_1RM_PERCENT_RANGE: Tuple[float, float] = (0.65, 0.80)


class TrainingPlanOptimiser:
    def __init__(self, request: GeneratePlanRequest):
        self.request = request
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Filter exercises by available equipment
        self.available_exercises: List[Exercise] = [
            ex for ex in EXERCISES if ex.equipment in self.request.equipment
        ]

        # Only consider days the user can train on
        self.days: List[Weekday] = sorted(
            self.request.available_days, key=lambda d: WEEKDAY_ORDER[d]
        )

    def solve(self) -> GeneratePlanResponse:
        # Decision variables:
        # x[(day, i)] = 1 if exercise i is scheduled on that day
        x: Dict[Tuple[Weekday, int], cp_model.IntVar] = {}
        for day in self.days:
            for i in range(len(self.available_exercises)):
                x[(day, i)] = self.model.NewBoolVar(f"x_{day}_{i}")

        # Constraint: total session time per day must not exceed user limit
        for day in self.days:
            self.model.Add(
                sum(
                    x[(day, i)] * self.available_exercises[i].duration_minutes
                    for i in range(len(self.available_exercises))
                )
                <= self.request.session_duration_minutes
            )

        # Constraint: every available day must have at least one exercise
        for day in self.days:
            self.model.Add(
                sum(x[(day, i)] for i in range(len(self.available_exercises))) >= 1
            )

        # Objective: maximise total number of exercises selected
        self.model.Maximize(
            sum(x[(day, i)] for day in self.days for i in range(len(self.available_exercises)))
        )

        status = self.solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise InfeasiblePlanError("Unable to generate a feasible training plan.")

        # Convert solver output into API response format
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
        # All exercises use the same neutral intensity in this version
        intensity = DEFAULT_INTENSITY

        # Compute weight range if the exercise is linked to a 1RM
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
