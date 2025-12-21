from ortools.sat.python import cp_model
from typing import List, Dict, Tuple, Optional

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

# 
# max is user-declared only and used to trigger deload solver only goes to high 
FATIGUE_INPUT_SCORE = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "max": 3,
}


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
        # fatigue is not inferred by the optimiser, its a user input only
        # optimiser never escalates fatigue beyond HIGH (MAX just triggers deload)
        deload_week = any(
            mg != CARDIO_GROUP and lvl.value == "max"
            for mg, lvl in self.request.fatigue_levels.items()
        )
        
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

        # constraint limit hitting the same muscle group more than once 
       
        per_muscle_cap = 2
        for day in self.days:
            for mg in MuscleGroup:
                if mg == CARDIO_GROUP:
                    continue
                idxs = [i for i, ex in enumerate(self.available_exercises) if ex.muscle_group == mg]
                if idxs:
                    self.model.Add(sum(x[(day, i)] for i in idxs) <= per_muscle_cap)

        # constraint avoid hitting the same mg on back to back days
       
        muscle_used: Dict[Tuple[Weekday, MuscleGroup], cp_model.IntVar] = {}
        for day in self.days:
            for mg in MuscleGroup:
                if mg == CARDIO_GROUP:
                    continue
                idxs = [i for i, ex in enumerate(self.available_exercises) if ex.muscle_group == mg]
                y = self.model.NewBoolVar(f"muscle_{day}_{mg}")
                muscle_used[(day, mg)] = y

                if not idxs:
                    self.model.Add(y == 0)
                    continue

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
                y1 = muscle_used[(day, mg)]
                y2 = muscle_used[(next_day, mg)]
                self.model.Add(y1 + y2 <= 1)

        # hard constraint weekly split based on available days
        base_coverage = [
            MuscleGroup.CHEST,
            MuscleGroup.BACK,
            MuscleGroup.LEGS,
            MuscleGroup.SHOULDERS,
        ]

        mg_has_exercise: Dict[MuscleGroup, bool] = {}
        for mg in base_coverage:
            mg_has_exercise[mg] = any(ex.muscle_group == mg for ex in self.available_exercises)

        week_used: Dict[MuscleGroup, cp_model.IntVar] = {}
        for mg in base_coverage:
            w = self.model.NewBoolVar(f"week_{mg}")
            week_used[mg] = w
            self.model.AddMaxEquality(w, [muscle_used[(day, mg)] for day in self.days])

        available_days = len(self.days)
        if available_days == 1:
            d = self.days[0]
            for mg in base_coverage:
                if mg_has_exercise[mg]:
                    self.model.Add(muscle_used[(d, mg)] == 1)

        if available_days == 2:
            d0, d1 = self.days[0], self.days[1]
            split = self.model.NewBoolVar("two_day_split")

            front_day = [MuscleGroup.CHEST, MuscleGroup.LEGS]
            back_day = [MuscleGroup.BACK, MuscleGroup.SHOULDERS]

            for mg in front_day:
                if not mg_has_exercise.get(mg, False):
                    continue
                self.model.Add(muscle_used[(d0, mg)] == 1).OnlyEnforceIf(split)
                self.model.Add(muscle_used[(d1, mg)] == 1).OnlyEnforceIf(split.Not())

            for mg in back_day:
                if not mg_has_exercise.get(mg, False):
                    continue
                self.model.Add(muscle_used[(d1, mg)] == 1).OnlyEnforceIf(split)
                self.model.Add(muscle_used[(d0, mg)] == 1).OnlyEnforceIf(split.Not())

        if available_days == 3:
            for mg in [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.LEGS]:
                if mg_has_exercise.get(mg, False):
                    self.model.Add(week_used[mg] == 1)

        if available_days >= 4:
            for mg in base_coverage:
                if mg_has_exercise[mg]:
                    self.model.Add(week_used[mg] == 1)

        #soft constraint depending on goal bias certain exercise 
        
        def _fatigue_penalty(mg: MuscleGroup) -> int:
            lvl = self.request.fatigue_levels.get(mg)
            if lvl is None:
                return 0
            score = FATIGUE_INPUT_SCORE.get(lvl.value, 0)
            # cap solver penalty at HIGH (MAX does not make it worse, it just triggers deload)
            return min(score, FATIGUE_INPUT_SCORE["high"])

        def _base_weight(ex: Exercise) -> int:
            if self.request.training_goal == TrainingGoal.STRENGTH:
                if ex.muscle_group == CARDIO_GROUP:
                    return 1
                return 5 if ex.is_compound else 3
            if self.request.training_goal == TrainingGoal.HYPERTROPHY:
                if ex.muscle_group == CARDIO_GROUP:
                    return 1
                return 3 if not ex.is_compound else 2
            if self.request.training_goal == TrainingGoal.FAT_LOSS:
                return 5 if ex.muscle_group == CARDIO_GROUP else 2
            if self.request.training_goal == TrainingGoal.GENERAL_FITNESS:
                return 2
            return 1

        def _exercise_weight(ex: Exercise) -> int:
            base = _base_weight(ex)
            penalty = _fatigue_penalty(ex.muscle_group)
            w = max(1, base - penalty)
            if deload_week and ex.is_compound and ex.muscle_group != CARDIO_GROUP:
                w = max(1, w - 3)
            return w

        # compound diminishing returns was getting the solver picking the same compound lift over and over again
        compound_count: Dict[Weekday, cp_model.IntVar] = {}
        for day in self.days:
            c = self.model.NewIntVar(0, len(self.available_exercises), f"compound_count_{day}")
            compound_count[day] = c
            self.model.Add(
                c
                == sum(
                    x[(day, i)]
                    for i, ex in enumerate(self.available_exercises)
                    if ex.is_compound
                )
            )

        compound_penalty = 1
        if deload_week:
            compound_penalty = 3

        self.model.Maximize(
            sum(
                x[(day, i)] * _exercise_weight(self.available_exercises[i])
                for day in self.days
                for i in range(len(self.available_exercises))
            )
            - compound_penalty * sum(compound_count[day] for day in self.days)
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
                    exercises_for_day.append(self._format_exercise(ex, deload_week))
            week_plan[day] = exercises_for_day

        return GeneratePlanResponse(
            training_goal=self.request.training_goal,
            deload_week=deload_week,
            week_plan=week_plan,
            fatigue_summary=self.request.fatigue_levels,
        )

    def _format_exercise(self, ex: Exercise, deload_week: bool) -> ExercisePlan:
        fatigue_level = self.request.fatigue_levels.get(ex.muscle_group)
        fatigue_value = 0
        if fatigue_level is not None:
            fatigue_value = FATIGUE_INPUT_SCORE.get(fatigue_level.value, 0)

        intensity = DEFAULT_INTENSITY
        rep_range = DEFAULT_REP_RANGE
        pct_range: Optional[Tuple[float, float]] = DEFAULT_1RM_PERCENT_RANGE

        if deload_week:
            intensity = IntensityLevel.LOW
            rep_range = "10-15"
            pct_range = (0.5, 0.65)
        else:
            if ex.muscle_group == CARDIO_GROUP:
                intensity = IntensityLevel.LOW
                rep_range = "10-15"
                pct_range = None
            elif self.request.training_goal == TrainingGoal.STRENGTH:
                if ex.is_compound:
                    intensity = IntensityLevel.HIGH
                    rep_range = "3-5"
                    pct_range = (0.8, 0.9)
                else:
                    intensity = IntensityLevel.MEDIUM
                    rep_range = "6-10"
                    pct_range = (0.65, 0.8)
            elif self.request.training_goal == TrainingGoal.HYPERTROPHY:
                intensity = IntensityLevel.MEDIUM
                rep_range = "6-10"
                pct_range = (0.65, 0.8)
            elif self.request.training_goal == TrainingGoal.FAT_LOSS:
                intensity = IntensityLevel.LOW
                rep_range = "10-15"
                pct_range = (0.5, 0.65)
            else:
                intensity = IntensityLevel.MEDIUM
                rep_range = "6-10"
                pct_range = (0.65, 0.8)

            # fatigue overrides
            if ex.muscle_group != CARDIO_GROUP:
                if fatigue_value == 1 and pct_range is not None:
                    low_pct, high_pct = pct_range
                    pct_range = (max(0.4, low_pct - 0.05), high_pct)
                if fatigue_value >= 2:
                    if intensity == IntensityLevel.HIGH:
                        intensity = IntensityLevel.MEDIUM
                    elif intensity == IntensityLevel.MEDIUM:
                        intensity = IntensityLevel.LOW
                    if pct_range is not None:
                        low_pct, high_pct = pct_range
                        pct_range = (max(0.4, low_pct - 0.1), max(0.45, high_pct - 0.1))

        # get a weight range based on the 1RM todo get 1rm from req 
        weight_range = None
        if ex.muscle_group != CARDIO_GROUP and ex.primary_1rm_link and pct_range is not None:
            one_rm_value = getattr(self.request.one_rep_maxes, ex.primary_1rm_link)
            low_pct, high_pct = pct_range

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
            rep_range=rep_range,
            weight_range_kg=weight_range,
        )
