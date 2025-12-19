from pydantic import BaseModel, Field
from typing import List, Dict, Set, Optional
from enum import Enum

class TrainingGoal(str, Enum):
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    FAT_LOSS = "fat_loss"
    GENERAL_FITNESS = "general_fitness"

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

class IntensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class FatigueLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"

class OneRepMaxes(BaseModel):
    squat_1rm: float = Field(..., gt=0)
    bench_1rm: float = Field(..., gt=0)
    deadlift_1rm: float = Field(..., gt=0)

class WeightRangeKg(BaseModel):
    min: float
    max: float

class GeneratePlanRequest(BaseModel):
    training_goal: TrainingGoal
    available_days: Set[Weekday]
    session_duration_minutes: int = Field(..., ge=30, le=90)
    equipment: Set[Equipment]
    one_rep_maxes: OneRepMaxes
    fatigue_levels: Dict[MuscleGroup, FatigueLevel]

class ExercisePlan(BaseModel):
    name: str
    muscle_group: MuscleGroup
    equipment: Equipment
    intensity_level: IntensityLevel
    rep_range: str
    weight_range_kg: Optional[WeightRangeKg] = None

class GeneratePlanResponse(BaseModel):
    training_goal: TrainingGoal
    deload_week: bool
    week_plan: Dict[Weekday, List[ExercisePlan]]
    fatigue_summary: Dict[MuscleGroup, FatigueLevel]

