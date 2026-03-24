from itertools import product
from collections import Counter
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
    PrimaryLiftKey,
    OneRepMaxes
)
from .weight_eval_engine import TrainingPlanOptimiser,InfeasiblePlanError


ALL_DAYS = [
    Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY,
    Weekday.THURSDAY, Weekday.FRIDAY, Weekday.SATURDAY,
]
 
GOALS = [TrainingGoal.HYPERTROPHY, TrainingGoal.STRENGTH, TrainingGoal.FAT_LOSS, TrainingGoal.GENERAL_FITNESS]
TIMES = [45, 60, 90]
DUMMY_1RMS = OneRepMaxes(squat_1rm=100, bench_1rm=80, deadlift_1rm=120, ohp_1rm=50)

PUSH_PATTERNS = {MovementPattern.HORIZONTAL_PUSH, MovementPattern.VERTICAL_PUSH}
PULL_PATTERNS = {MovementPattern.HORIZONTAL_PULL, MovementPattern.VERTICAL_PULL}
SQUAT_PATTERNS = {MovementPattern.SQUAT, MovementPattern.SINGLE_LEG}
HINGE_PATTERNS = {MovementPattern.HINGE}
exName_pattern={ex.name: ex.pattern for ex in EXERCISES}

grid_weights={"stimulus_scale":[5,10,15],
    "arms_bonus":[3,8,10],
    "under_penalty":[3,5,7],
    "over_penalty":[1,3,5],
    "base_repeat_penalty":[3,8,12],
    "filler_base_penalty":[10,25,35]}


def build_scenarios()->list[dict]:
    scenarios=[]
    equiment_set = [
        ("full_gym", {Equipment.BARBELL, Equipment.DUMBBELL, Equipment.MACHINE}),
        ("bodyweight_only", {Equipment.BODYWEIGHT}),
        ("dumbbell", {Equipment.DUMBBELL}),
    ]

    for n_days, (equ_name, equ_set), goal, duration in product(range(1, 7), equiment_set, GOALS, TIMES):
        days=set(ALL_DAYS[:n_days])
        include_cardio=goal in [TrainingGoal.FAT_LOSS, TrainingGoal.GENERAL_FITNESS]

        request=GeneratePlanRequest(
            training_goal=goal,
            available_days=days,
            session_duration_minutes=duration,
            equipment=equ_set,
            include_cardio=include_cardio,
            one_rep_maxes=DUMMY_1RMS,
        )

        scenarios.append({
            "request":request,
            "label":f"{equ_name}_{goal}_{duration}min_{n_days}days",
        })
    return scenarios

def score_time_fill(response:GeneratePlanResponse,session_target:int)->float:
        total_time=0
        for day in response.week_plan.values():
            for ex in day:
                total_time+=ex.sets*ex.work_minutes+(ex.sets-1)*ex.rest_minutes
        total_target=session_target*len(response.week_plan)
        return max(0,1-abs(total_time-total_target)/total_target)

def score_variety(response:GeneratePlanResponse)->float:
        name=[]
        for exercise in response.week_plan.values():
            for ex in exercise:
                name.append(ex.name)

        if not name:
            return 0.0
        repeat=0
        counter=Counter(name)
        for c in counter.values():
            if c>1:
                    repeat+=c-1
        return max(0.0,1.0-repeat/len(name))
    
def score_mg_coverage(response:GeneratePlanResponse)->float:
        if response.training_goal in [TrainingGoal.HYPERTROPHY, TrainingGoal.STRENGTH]:
            expected_coverage={MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.LEGS, 
                                MuscleGroup.SHOULDERS, MuscleGroup.ARMS}
        elif response.training_goal == TrainingGoal.FAT_LOSS:
            expected_coverage={MuscleGroup.CARDIO, MuscleGroup.LEGS,MuscleGroup.CORE}

        else:
            expected_coverage={MuscleGroup.LEGS, MuscleGroup.BACK, MuscleGroup.CHEST,
                                MuscleGroup.SHOULDERS}
        actual_coverage=set()
        for exercise in response.week_plan.values():
            for ex in exercise:
                actual_coverage.add(ex.muscle_group)
        return len(actual_coverage & expected_coverage)/len(expected_coverage)

def score_balance(response:GeneratePlanResponse)->float:
        push_n=0
        pull_n=0
        legs_n=0
        hinge_n=0
        for exercise in response.week_plan.values():
            for ex in exercise:
                pat=exName_pattern[ex.name]
                if pat is None:
                    continue
                if pat in PUSH_PATTERNS:
                    push_n+=1
                elif pat in PULL_PATTERNS:
                    pull_n+=1
                elif pat in SQUAT_PATTERNS:
                    legs_n+=1
                elif pat in HINGE_PATTERNS:
                    hinge_n+=1
        
        pp = 1.0 - abs(push_n - pull_n) / max(push_n, pull_n, 1)
        sh = 1.0 - abs(legs_n - hinge_n) / max(legs_n, hinge_n, 1)
        return (pp+sh)/2.0
    
def score_plan(response:GeneratePlanResponse,request:GeneratePlanRequest)->dict:
    tf=score_time_fill(response,request.session_duration_minutes)
    var=score_variety(response)
    mg=score_mg_coverage(response)
    bal=score_balance(response)
    overall=(tf+var+mg+bal)/4.0
    return {
        "time_fill":tf,
        "variety":var,
        "mg_coverage":mg,
        "balance":bal,
        "overall":overall
    }


def build_weight_combo():
    keys=list(grid_weights.keys())
    combos=[]
    for i in product(*grid_weights.values()):
        combos.append(dict(zip(keys,i)))
    return combos

def run_grid_search():
    scenarios=build_scenarios()
    weight_combos=build_weight_combo()
    results=[]
    for comboidx,weights in enumerate(weight_combos):
        combo_scores=[]
        infeasible_count=0

        for scenario in scenarios:
            try:
                optimiser=TrainingPlanOptimiser(scenario["request"],weights)
                response=optimiser.solve()
                score=score_plan(response,scenario["request"])
                combo_scores.append(score["overall"])
            except InfeasiblePlanError:
                infeasible_count+=1
                combo_scores.append(0.0)
        avg_score=sum(combo_scores)/len(combo_scores)
        min_score=min(combo_scores)

        results.append({
            "weights":weights,
            "avg_score":avg_score,
            "infeasible_count":infeasible_count,
            "combo_idx":comboidx,
            "min_score":min_score,
        })
        if (comboidx+1) % 50 == 0:
            print(f"Processed {comboidx+1} of {len(weight_combos)} weight combinations")

    results.sort(key=lambda x: (x["avg_score"], x["min_score"]), reverse=True)

    print("top ten results:")
    for i,result in enumerate(results[:10]):
            w=result["weights"]
            print(
            f"{i+1}.\n"
            f"  stimulus_scale: {w['stimulus_scale']}\n"
            f"  arms_bonus: {w['arms_bonus']}\n"
            f"  under_penalty: {w['under_penalty']}\n"
            f"  over_penalty: {w['over_penalty']}\n"
            f"  base_repeat_penalty: {w['base_repeat_penalty']}\n"
            f"  filler_base_penalty: {w['filler_base_penalty']}\n"
            f"  avg: {result['avg_score']:.2f}, min: {result['min_score']:.2f}")
    print("bottom 5")
    for i,result in enumerate(results[-5:]):
            w=result["weights"]
            print(
            f"{i+1}.\n"
            f"  stimulus_scale: {w['stimulus_scale']}\n"
            f"  arms_bonus: {w['arms_bonus']}\n"
            f"  under_penalty: {w['under_penalty']}\n"
            f"  over_penalty: {w['over_penalty']}\n"
            f"  base_repeat_penalty: {w['base_repeat_penalty']}\n"
            f"  filler_base_penalty: {w['filler_base_penalty']}\n"
            f"  avg: {result['avg_score']:.2f}, min: {result['min_score']:.2f}")


if __name__ == "__main__":
    run_grid_search()
        
           



