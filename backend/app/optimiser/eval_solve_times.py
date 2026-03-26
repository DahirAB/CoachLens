import csv
import time
from itertools import product

from .data import EXERCISES
from ..models.schemas import (
    GeneratePlanRequest,
    TrainingGoal,
    Weekday,
    Equipment,
    OneRepMaxes,
)
from .weight_eval_engine import TrainingPlanOptimiser, InfeasiblePlanError

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
    "arms_bonus": 3,
    "under_penalty": 5,
    "over_penalty": 1,
    "base_repeat_penalty": 12,
    "filler_base_penalty": 10,
}


def count_available_exercises(equ_set, include_cardio):
    allowed = equ_set | {Equipment.BODYWEIGHT}
    count = 0
    for ex in EXERCISES:
        if ex.equipment not in allowed:
            continue
        if ex.muscle_group.value == "cardio" and not include_cardio:
            continue
        count += 1
    return count


def run_solve_time_benchmark():
    rows = []

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

        n_exercises = count_available_exercises(equ_set, include_cardio)
        n_variables = n_days * n_exercises * 2

        solve_time = 0.0
        status = "feasible"
        total_exercises_selected = 0

        try:
            t0 = time.perf_counter()
            optimiser = TrainingPlanOptimiser(request, BEST_WEIGHTS)
            response = optimiser.solve()
            solve_time = time.perf_counter() - t0

            for day_exercises in response.week_plan.values():
                total_exercises_selected += len(day_exercises)
        except InfeasiblePlanError:
            status = "infeasible"
        except Exception as e:
            status = f"error: {e}"

        rows.append({
            "goal": goal.value,
            "equipment": equ_name,
            "duration_min": duration,
            "n_days": n_days,
            "n_available_exercises": n_exercises,
            "n_decision_variables": n_variables,
            "exercises_selected": total_exercises_selected,
            "solve_time_s": round(solve_time, 4),
            "status": status,
        })

    with open("solve_times.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    feasible_rows = [r for r in rows if r["status"] == "feasible"]

    if feasible_rows:
        times = [r["solve_time_s"] for r in feasible_rows]
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        slowest = max(feasible_rows, key=lambda r: r["solve_time_s"])

        print(f"\nSolve Time Benchmark Results")
        print(f"Feasible scenarios: {len(feasible_rows)}")
        print(f"Average solve time: {avg_time:.3f}s")
        print(f"Min solve time: {min_time:.4f}s")
        print(f"Max solve time: {max_time:.3f}s")
        print(f"Slowest config: {slowest['goal']} / {slowest['equipment']} / "
              f"{slowest['duration_min']}min / {slowest['n_days']}days "
              f"({slowest['solve_time_s']:.3f}s)")

        by_days = {}
        for r in feasible_rows:
            d = r["n_days"]
            by_days.setdefault(d, []).append(r["solve_time_s"])

        print(f"\nAverage solve time by day count:")
        for d in sorted(by_days):
            avg = sum(by_days[d]) / len(by_days[d])
            print(f"  {d} days: {avg:.3f}s ({len(by_days[d])} scenarios)")

        by_equip = {}
        for r in feasible_rows:
            e = r["equipment"]
            by_equip.setdefault(e, []).append(r["solve_time_s"])

        print(f"\nAverage solve time by equipment:")
        for e in sorted(by_equip):
            avg = sum(by_equip[e]) / len(by_equip[e])
            print(f"  {e}: {avg:.3f}s")

    print("\nSaved: solve_times.csv")


if __name__ == "__main__":
    run_solve_time_benchmark()
