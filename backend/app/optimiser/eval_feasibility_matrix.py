import csv
import time
from itertools import product
from collections import defaultdict

from .data import EXERCISES, Exercise, LiftTier, MovementPattern
from ..models.schemas import (
    GeneratePlanRequest,
    TrainingGoal,
    Weekday,
    MuscleGroup,
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
    "arms_bonus": 10,
    "under_penalty": 7,
    "over_penalty": 1,
    "base_repeat_penalty": 12,
    "filler_base_penalty": 10,
}


def run_feasibility_matrix():
    rows = []
    summary = defaultdict(lambda: {"total": 0, "infeasible": 0})

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

        feasible = True
        error_msg = ""
        solve_time = 0.0

        try:
            t0 = time.perf_counter()
            optimiser = TrainingPlanOptimiser(request, BEST_WEIGHTS)
            response = optimiser.solve()
            solve_time = time.perf_counter() - t0
        except InfeasiblePlanError as e:
            feasible = False
            error_msg = str(e)
        except Exception as e:
            feasible = False
            error_msg = f"unexpected: {e}"

        row = {
            "goal": goal.value,
            "equipment": equ_name,
            "duration_min": duration,
            "n_days": n_days,
            "feasible": feasible,
            "solve_time_s": round(solve_time, 3),
            "error": error_msg,
        }
        rows.append(row)

        for key in [
            f"goal:{goal.value}",
            f"equip:{equ_name}",
            f"duration:{duration}",
            f"days:{n_days}",
            f"{goal.value}_{equ_name}",
            f"{goal.value}_{duration}min",
            f"{goal.value}_{n_days}days",
            f"{equ_name}_{duration}min",
        ]:
            summary[key]["total"] += 1
            if not feasible:
                summary[key]["infeasible"] += 1

    with open("feasibility_matrix.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    infeasible_total = sum(1 for r in rows if not r["feasible"])
    feasible_total = total - infeasible_total

    print(f"\nFeasibility Matrix Results")
    print(f"Total scenarios: {total}")
    print(f"Feasible: {feasible_total} ({100*feasible_total/total:.1f}%)")
    print(f"Infeasible: {infeasible_total} ({100*infeasible_total/total:.1f}%)")

    print(f"\nBreakdown by dimension:")
    for key in sorted(summary.keys()):
        s = summary[key]
        rate = 100 * s["infeasible"] / s["total"] if s["total"] else 0
        if s["infeasible"] > 0:
            print(f"  {key}: {s['infeasible']}/{s['total']} infeasible ({rate:.0f}%)")

    summary_rows = []
    for key in sorted(summary.keys()):
        s = summary[key]
        summary_rows.append({
            "dimension": key,
            "total": s["total"],
            "infeasible": s["infeasible"],
            "feasible": s["total"] - s["infeasible"],
            "infeasible_rate": round(s["infeasible"] / s["total"], 3) if s["total"] else 0,
        })

    with open("feasibility_summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)

    print("\nSaved: feasibility_matrix.csv, feasibility_summary.csv")


if __name__ == "__main__":
    run_feasibility_matrix()
