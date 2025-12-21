from typing import Optional
from ..models.schemas import Equipment, MuscleGroup

class Exercise:
    def __init__(
        self,
        name: str,
        muscle_group: MuscleGroup,
        equipment: Equipment,
        is_compound: bool,
        duration_minutes: int,
        primary_1rm_link: Optional[str] = None, # squat_1rm, bench_1rm, deadlift_1rm
        weight_multiplier: float = 1.0 
    ):
        self.name = name
        self.muscle_group = muscle_group
        self.equipment = equipment
        self.is_compound = is_compound
        self.duration_minutes = duration_minutes
        self.primary_1rm_link = primary_1rm_link
        self.weight_multiplier = weight_multiplier

EXERCISES = [
    # Legs
    Exercise("Barbell Back Squat", MuscleGroup.LEGS, Equipment.BARBELL, True, 20, "squat_1rm", 1.0),
    Exercise("Dumbbell Lunges", MuscleGroup.LEGS, Equipment.DUMBBELL, False, 15, "squat_1rm", 0.4),
    Exercise("Leg Press", MuscleGroup.LEGS, Equipment.MACHINE, False, 15, "squat_1rm", 0.8),
    Exercise("Leg Extension", MuscleGroup.LEGS, Equipment.MACHINE, False, 10, "squat_1rm", 0.3),
    Exercise("Bodyweight Squats", MuscleGroup.LEGS, Equipment.BODYWEIGHT, False, 10),
    
    # Chest
    Exercise("Barbell Bench Press", MuscleGroup.CHEST, Equipment.BARBELL, True, 20, "bench_1rm", 1.0),
    Exercise("Dumbbell Flyes", MuscleGroup.CHEST, Equipment.DUMBBELL, False, 10, "bench_1rm", 0.3),
    Exercise("Chest Press Machine", MuscleGroup.CHEST, Equipment.MACHINE, False, 15, "bench_1rm", 0.7),
    Exercise("Pushups", MuscleGroup.CHEST, Equipment.BODYWEIGHT, False, 10),
    
    # Back
    Exercise("Barbell Deadlift", MuscleGroup.BACK, Equipment.BARBELL, True, 20, "deadlift_1rm", 1.0),
    Exercise("Barbell Row", MuscleGroup.BACK, Equipment.BARBELL, True, 20, "deadlift_1rm", 0.6),
    Exercise("Lat Pulldown", MuscleGroup.BACK, Equipment.MACHINE, False, 15, "deadlift_1rm", 0.5),
    Exercise("Pullups", MuscleGroup.BACK, Equipment.BODYWEIGHT, False, 15),
    
    # Shoulders
    Exercise("Overhead Press", MuscleGroup.SHOULDERS, Equipment.BARBELL, True, 20, "bench_1rm", 0.6),
    Exercise("Lateral Raises", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, False, 10, "bench_1rm", 0.1),

    # Arms
    Exercise("Dumbbell Bicep Curl", MuscleGroup.ARMS, Equipment.DUMBBELL, False, 10, "bench_1rm", 0.1),
    Exercise("Tricep Pushdown", MuscleGroup.ARMS, Equipment.MACHINE, False, 10, "bench_1rm", 0.15),

    # Core
    Exercise("Plank", MuscleGroup.CORE, Equipment.BODYWEIGHT, False, 10),
    
    # Cardio
    # cardio exercises are gonna be treated differently to others later i wont add things like fatigue 
    # but does NOT require cardio equipment.
    Exercise("Outdoor Run", MuscleGroup.CARDIO, Equipment.BODYWEIGHT, False, 20),
    Exercise("Brisk Walk", MuscleGroup.CARDIO, Equipment.BODYWEIGHT, False, 20),
    Exercise("Treadmill Run", MuscleGroup.CARDIO, Equipment.CARDIO, False, 20),
    Exercise("Cycling", MuscleGroup.CARDIO, Equipment.CARDIO, False, 20),
]

MUSCLE_GROUPS = [mg for mg in MuscleGroup]

