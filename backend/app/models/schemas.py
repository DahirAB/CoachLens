from pydantic import BaseModel, Field
from typing import List, Dict, Set, Optional
from enum import Enum


class TrainingGoal(str, Enum):
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    FAT_LOSS = "fat_loss"
    GENERAL_FITNESS = "general_fitness"


class PrimaryLiftKey(str, Enum):
    SQUAT = "squat_1rm"
    BENCH = "bench_1rm"
    DEADLIFT = "deadlift_1rm"
    OHP = "ohp_1rm"

class Weekday(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class Equipment(str, Enum):
    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    MACHINE = "machine"
    BODYWEIGHT = "bodyweight"
    CARDIO = "cardio"

class MuscleGroup(str, Enum):
    LEGS = "legs"
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    CORE = "core"
    CARDIO = "cardio"




class SplitType(str, Enum):
    FULL_BODY = "full_body"
    UPPER = "upper"
    LOWER = "lower"
    PUSH = "push"
    PULL = "pull"
    LEGS = "legs"


class OneRepMaxes(BaseModel):
    squat_1rm: float = Field(..., gt=0)
    bench_1rm: float = Field(..., gt=0)
    deadlift_1rm: float = Field(..., gt=0)
    ohp_1rm: float = Field(..., gt=0)

class WeightRangeKg(BaseModel):
    min: float
    max: float

class OnboardingRequest(BaseModel):
    training_goal: str
    available_days: List[str]
    session_duration_min: int
    equipment: List[str]
    include_cardio: bool = False
    squat_1rm: float=Field(..., gt=0)
    bench_1rm: float=Field(..., gt=0)
    deadlift_1rm: float=Field(..., gt=0)
    ohp_1rm: float=Field(..., gt=0)
    required_primary_lifts: Optional[List[str]] = None
    excluded_exercises: Optional[List[str]] = None
    first_name: str


class GeneratePlanRequest(BaseModel):
    training_goal: TrainingGoal
    available_days: Set[Weekday]
    session_duration_minutes: int = Field(..., ge=30, le=90)
    equipment: Set[Equipment]
    one_rep_maxes: OneRepMaxes
    required_primary_lifts: Set[PrimaryLiftKey] = Field(default_factory=set)
    excluded_exercises: Set[str] = Field(default_factory=set)
    include_cardio: bool = False

class ExercisePlan(BaseModel):
    name: str
    muscle_group: MuscleGroup
    equipment: Equipment
    rep_range: str
    sets: int = Field(..., ge=1)
    work_minutes: int = Field(..., ge=0)
    rest_minutes: int = Field(..., ge=0)
    weight_range_kg: Optional[WeightRangeKg] = None
    weight_display: Optional[str] = None

class GeneratePlanResponse(BaseModel):
    training_goal: TrainingGoal
    inferred_split: Dict[Weekday, SplitType]
    week_plan: Dict[Weekday, List[ExercisePlan]]
