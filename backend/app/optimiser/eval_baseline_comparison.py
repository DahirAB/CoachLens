import csv
import random
from itertools import product
from collections import defaultdict

from .data import EXERCISES, Exercise, LiftTier, MovementPattern
from ..models.schemas import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    TrainingGoal,
    Weekday,
    ExercisePlan,
    WeightRangeKg,
    MuscleGroup,
    Equipment,
    SplitType,
    OneRepMaxes,
)
from .weight_eval_engine import TrainingPlanOptimiser, InfeasiblePlanError
from .gridWsearch import score_plan

ALL_DAYS = [
    Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY,
    Weekday.THURSDAY, Weekday.FRIDAY, Weekday.SATURDAY,
]

GOALS = [TrainingGoal.HYPERTROPHY, TrainingGoal.STRENGTH, TrainingGoal.FAT_LOSS, TrainingGoal.GENERAL_FITNESS]
TIMES = [45, 60, 90]
DUMMY_1RMS = OneRepMaxes(squat_1rm=100, bench_1rm=80, deadlift_1rm=120, ohp_1rm=50)

EQUIPMENT_SETS = [
    ("full_gym", {Equipment.BARBELL, Equipment.DUMBBELL, Equipment.MACHINE}),
    ("bodyweight_only", {Equipment.BODYWEIGHT}),
    ("dumbbell", {Equipment.DUMBBELL}),
]

BEST_WEIGHTS = {
    "stimulus_scale": 10,
    "arms_bonus": 10,
    "under_penalty": 7,
    "over_penalty": 1,
    "base_repeat_penalty": 12,
    "filler_base_penalty": 10,
}

PUSH_PAT = {MovementPattern.HORIZONTAL_PUSH, MovementPattern.VERTICAL_PUSH}
PULL_PAT = {MovementPattern.HORIZONTAL_PULL, MovementPattern.VERTICAL_PULL}
LEGS_PAT = {MovementPattern.SQUAT, MovementPattern.SINGLE_LEG}
HINGE_PAT = {MovementPattern.HINGE}


def get_exercise_time(ex, goal):
    if ex.muscle_group == MuscleGroup.CARDIO:
        return 15
    if ex.muscle_group == MuscleGroup.CORE:
        return 2 * 3 + 1 * 2
    if goal == TrainingGoal.STRENGTH:
        if ex.tier == LiftTier.MAIN:
            return 2 * 4 + 4 * 3
        if ex.tier == LiftTier.SECONDARY:
            return 2 * 3 + 3 * 2
        return 2 * 3 + 2 * 2
    if goal == TrainingGoal.HYPERTROPHY:
        if ex.tier in (LiftTier.MAIN, LiftTier.SECONDARY, LiftTier.ACCESSORY):
            return 2 * 4 + 2 * 3
        return 1 * 3 + 1 * 2
    return 1 * 3 + 1 * 2


def make_exercise_plan(ex, goal):
    if ex.muscle_group == MuscleGroup.CARDIO:
        return ExercisePlan(
            name=ex.name, muscle_group=ex.muscle_group, equipment=ex.equipment,
            rep_range="15 Minutes", sets=1, work_minutes=15, rest_minutes=0,
            weight_range_kg=None, weight_display=None,
        )
    if ex.muscle_group == MuscleGroup.CORE:
        return ExercisePlan(
            name=ex.name, muscle_group=ex.muscle_group, equipment=ex.equipment,
            rep_range="30-60s", sets=3, work_minutes=2, rest_minutes=1,
            weight_range_kg=None, weight_display=None,
        )
    sets = 3
    return ExercisePlan(
        name=ex.name, muscle_group=ex.muscle_group, equipment=ex.equipment,
        rep_range="6-10", sets=sets, work_minutes=2, rest_minutes=2,
        weight_range_kg=None, weight_display=None,
    )


def generate_random_plan(request):
    allowed_equipment = request.equipment | {Equipment.BODYWEIGHT}
    include_cardio = request.include_cardio

    available = []
    for ex in EXERCISES:
        if ex.equipment not in allowed_equipment:
            continue
        if ex.muscle_group == MuscleGroup.CARDIO and not include_cardio:
            continue
        available.append(ex)

    if not available:
        return None

    days = sorted(request.available_days, key=lambda d: list(Weekday).index(d))
    week_plan = {}

    for day in days:
        pool = list(available)
        random.shuffle(pool)
        day_exercises = []
        time_used = 0
        used_muscles = set()

        for ex in pool:
            ex_time = get_exercise_time(ex, request.training_goal)
            if time_used + ex_time > request.session_duration_minutes:
                continue
            day_exercises.append(make_exercise_plan(ex, request.training_goal))
            time_used += ex_time
            used_muscles.add(ex.muscle_group)

        week_plan[day] = day_exercises

    split_dict = {d: SplitType.FULL_BODY for d in days}

    return GeneratePlanResponse(
        training_goal=request.training_goal,
        inferred_split=split_dict,
        week_plan=week_plan,
    )


def run_baseline_comparison():
    random.seed(42)
    rows = []
    solver_scores = []
    baseline_scores = []
    baseline_runs_per_scenario = 20

    for n_days, (equ_name, equ_set), goal, duration in product(
        range(1, 7), EQUIPMENT_SETS, GOALS, TIMES
    ):
        days = set(ALL_DAYS[:n_days])
        include_cardio = goal in [TrainingGoal.FAT_LOSS, TrainingGoal.GENERAL_FITNESS]

        request = GeneratePlanRequest(
            training_goal=goal,
            available_days=days,
            session_duration_minutes=duration,
            equipment=equ_set,
            include_cardio=include_cardio,
            one_rep_maxes=DUMMY_1RMS,
        )

        solver_scores_list = []
        for _ in range(5):
            try:
                optimiser = TrainingPlanOptimiser(request, BEST_WEIGHTS)
                response = optimiser.solve()
                scores = score_plan(response, request)
                solver_scores_list.append(scores["overall"])
            except (InfeasiblePlanError, Exception):
                pass

        if solver_scores_list:
            solver_score = sum(solver_scores_list) / len(solver_scores_list)
            solver_std = (sum((s - solver_score)**2 for s in solver_scores_list) / len(solver_scores_list)) ** 0.5
        else:
            solver_score = None
            solver_std = None

        rand_scores_list = []
        for _ in range(baseline_runs_per_scenario):
            rand_response = generate_random_plan(request)
            if rand_response and any(len(exs) > 0 for exs in rand_response.week_plan.values()):
                rs = score_plan(rand_response, request)
                rand_scores_list.append(rs["overall"])
            else:
                rand_scores_list.append(0.0)

        avg_rand = sum(rand_scores_list) / len(rand_scores_list)
        best_rand = max(rand_scores_list)
        rand_std = (sum((s - avg_rand)**2 for s in rand_scores_list) / len(rand_scores_list)) ** 0.5

        row = {
            "goal": goal.value,
            "equipment": equ_name,
            "duration_min": duration,
            "n_days": n_days,
            "solver_score": round(solver_score, 4) if solver_score is not None else "infeasible",
            "solver_std": round(solver_std, 4) if solver_std is not None else "n/a",
            "baseline_avg_score": round(avg_rand, 4),
            "baseline_std": round(rand_std, 4),
            "baseline_best_score": round(best_rand, 4),
            "solver_wins": solver_score is not None and solver_score > avg_rand,
            "improvement_pct": round(100 * (solver_score - avg_rand) / avg_rand, 1) if solver_score and avg_rand > 0 else "n/a",
        }
        rows.append(row)

        if solver_score is not None:
            solver_scores.append(solver_score)
            baseline_scores.append(avg_rand)

    with open("baseline_comparison.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    wins = sum(1 for r in rows if r["solver_wins"] is True)
    losses = sum(1 for r in rows if r["solver_wins"] is False and r["solver_score"] != "infeasible")
    infeasible = sum(1 for r in rows if r["solver_score"] == "infeasible")

    print(f"\nBaseline Comparison Results")
    print(f"Total scenarios: {len(rows)}")
    print(f"Solver wins: {wins}")
    print(f"Baseline wins: {losses}")
    print(f"Solver infeasible: {infeasible}")

    if solver_scores:
        avg_solver = sum(solver_scores) / len(solver_scores)
        avg_baseline = sum(baseline_scores) / len(baseline_scores)
        improvement = 100 * (avg_solver - avg_baseline) / avg_baseline if avg_baseline > 0 else 0

        print(f"\nAverage solver score: {avg_solver:.4f}")
        print(f"Average baseline score: {avg_baseline:.4f}")
        print(f"Overall improvement: {improvement:.1f}%")

    by_goal = defaultdict(lambda: {"solver": [], "baseline": []})
    for r, sv, bv in zip(rows, solver_scores if solver_scores else [], baseline_scores if baseline_scores else []):
        if r["solver_score"] != "infeasible":
            by_goal[r["goal"]]["solver"].append(float(r["solver_score"]))
            by_goal[r["goal"]]["baseline"].append(float(r["baseline_avg_score"]))

    print(f"\nBreakdown by goal:")
    for goal in sorted(by_goal):
        s_avg = sum(by_goal[goal]["solver"]) / len(by_goal[goal]["solver"])
        b_avg = sum(by_goal[goal]["baseline"]) / len(by_goal[goal]["baseline"])
        imp = 100 * (s_avg - b_avg) / b_avg if b_avg > 0 else 0
        print(f"  {goal}: solver={s_avg:.3f} baseline={b_avg:.3f} improvement={imp:.1f}%")

    print("\nSaved: baseline_comparison.csv")


if __name__ == "__main__":
    run_baseline_comparison()
