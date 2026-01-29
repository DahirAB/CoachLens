from typing import Optional, List
from enum import Enum
from ..models.schemas import Equipment, MuscleGroup


class MovementPattern(str, Enum):
    SQUAT = "squat"
    HINGE = "hinge"
    HORIZONTAL_PUSH = "horizontal_push"
    VERTICAL_PUSH = "vertical_push"
    HORIZONTAL_PULL = "horizontal_pull"
    VERTICAL_PULL = "vertical_pull"
    SINGLE_LEG = "single_leg"
    SHOULDER_ISO = "shoulder_iso"
    ARMS = "arms"
    CORE = "core"
    CARDIO = "cardio"


class LiftTier(str, Enum):
    MAIN = "main"
    SECONDARY = "secondary"
    ACCESSORY = "accessory"
    ISOLATION = "isolation"
    CARDIO = "cardio"

class Exercise:
    def __init__(
        self,
        name: str,
        muscle_group: MuscleGroup,
        equipment: Equipment,
        is_compound: bool,
        pattern: MovementPattern,
        tier: LiftTier,
        secondary_muscles: Optional[List[MuscleGroup]] = None,
        primary_1rm_link: Optional[str] = None, # squat_1rm, bench_1rm, deadlift_1rm
        weight_multiplier: float = 1.0,
        family: Optional[str] = None,
    ):
        self.name = name
        self.muscle_group = muscle_group
        self.equipment = equipment
        self.is_compound = is_compound
        self.pattern = pattern
        self.tier = tier
        self.secondary_muscles = secondary_muscles or []
        self.primary_1rm_link = primary_1rm_link
        self.weight_multiplier = weight_multiplier
        self.family = family

EXERCISES = [
    # Legs
    Exercise("Barbell Front Squat", MuscleGroup.LEGS, Equipment.BARBELL, True, MovementPattern.SQUAT, LiftTier.MAIN, [MuscleGroup.CORE], "squat_1rm", 0.9, family="squat_pattern"),
    Exercise("Barbell Back Squat", MuscleGroup.LEGS, Equipment.BARBELL, True, MovementPattern.SQUAT, LiftTier.MAIN, [MuscleGroup.CORE], "squat_1rm", 1.0, family="squat_pattern"),
    Exercise("Dumbbell Lunges", MuscleGroup.LEGS, Equipment.DUMBBELL, False, MovementPattern.SINGLE_LEG, LiftTier.ACCESSORY, [MuscleGroup.CORE], None, 1.0, family="single_leg"),
    Exercise("Leg Press", MuscleGroup.LEGS, Equipment.MACHINE, False, MovementPattern.SQUAT, LiftTier.ACCESSORY, [], None, 1.0, family="squat_pattern"),
    Exercise("Leg Extension", MuscleGroup.LEGS, Equipment.MACHINE, False, MovementPattern.SQUAT, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Leg Curl", MuscleGroup.LEGS, Equipment.MACHINE, False, MovementPattern.HINGE, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Calf Raises", MuscleGroup.LEGS, Equipment.BODYWEIGHT, False, MovementPattern.SINGLE_LEG, LiftTier.ACCESSORY, [], None, 1.0, family="calf_raise"),
    Exercise("Dumbbell Calf Raises", MuscleGroup.LEGS, Equipment.DUMBBELL, False, MovementPattern.SINGLE_LEG, LiftTier.ACCESSORY, [], None, 1.0, family="calf_raise"),
    Exercise("Barbell Calf Raises", MuscleGroup.LEGS, Equipment.BARBELL, False, MovementPattern.SINGLE_LEG, LiftTier.ACCESSORY, [], None, 1.0, family="calf_raise"),
    Exercise("Bodyweight Squats", MuscleGroup.LEGS, Equipment.BODYWEIGHT, False, MovementPattern.SQUAT, LiftTier.ACCESSORY, [], None, 1.0, family="squat_pattern"),
    Exercise("Dumbbell Front Squat", MuscleGroup.LEGS, Equipment.DUMBBELL, False, MovementPattern.SQUAT, LiftTier.MAIN, [MuscleGroup.CORE], "squat_1rm", 0.45, family="squat_pattern"),
    Exercise("Glute Bridges", MuscleGroup.LEGS, Equipment.BODYWEIGHT, False, MovementPattern.HINGE, LiftTier.ACCESSORY, [MuscleGroup.CORE], None, 1.0, family="hinge_pattern"),

    # Chest
    Exercise("Barbell Bench Press", MuscleGroup.CHEST, Equipment.BARBELL, True, MovementPattern.HORIZONTAL_PUSH, LiftTier.MAIN, [MuscleGroup.ARMS], "bench_1rm", 1.0, family="flat_press"),
    Exercise("Flat Dumbbell Press", MuscleGroup.CHEST, Equipment.DUMBBELL, True, MovementPattern.HORIZONTAL_PUSH, LiftTier.MAIN, [MuscleGroup.ARMS], "bench_1rm", 0.85, family="flat_press"),
    Exercise("Incline Dumbbell Press", MuscleGroup.CHEST, Equipment.DUMBBELL, True, MovementPattern.HORIZONTAL_PUSH, LiftTier.SECONDARY, [MuscleGroup.SHOULDERS, MuscleGroup.ARMS], None, 1.0, family="incline_press"),
    Exercise("Barbell Incline Bench Press", MuscleGroup.CHEST, Equipment.BARBELL, True, MovementPattern.HORIZONTAL_PUSH, LiftTier.SECONDARY, [MuscleGroup.SHOULDERS, MuscleGroup.ARMS], None, 1.0, family="incline_press"),
    Exercise("Dumbbell Flyes", MuscleGroup.CHEST, Equipment.DUMBBELL, False, MovementPattern.HORIZONTAL_PUSH, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Chest Press Machine", MuscleGroup.CHEST, Equipment.MACHINE, False, MovementPattern.HORIZONTAL_PUSH, LiftTier.ACCESSORY, [], None, 1.0, family="flat_press"),
    Exercise("Pushups", MuscleGroup.CHEST, Equipment.BODYWEIGHT, False, MovementPattern.HORIZONTAL_PUSH, LiftTier.ACCESSORY, [], None, 1.0, family="flat_press"),
    Exercise("Pike Pushups", MuscleGroup.SHOULDERS, Equipment.BODYWEIGHT, False, MovementPattern.VERTICAL_PUSH, LiftTier.ACCESSORY, [MuscleGroup.CHEST], None, 1.0, family="vertical_push"),
    
    # Back
    Exercise("Barbell Deadlift", MuscleGroup.BACK, Equipment.BARBELL, True, MovementPattern.HINGE, LiftTier.MAIN, [MuscleGroup.LEGS, MuscleGroup.CORE], "deadlift_1rm", 1.0, family="deadlift_pattern"),
    Exercise("Rack Pull Deadlift", MuscleGroup.BACK, Equipment.BARBELL, True, MovementPattern.HINGE, LiftTier.MAIN, [MuscleGroup.LEGS, MuscleGroup.CORE], "deadlift_1rm", 1.1, family="deadlift_pattern"),
    Exercise("Raised Deadlift", MuscleGroup.BACK, Equipment.BARBELL, True, MovementPattern.HINGE, LiftTier.MAIN, [MuscleGroup.LEGS, MuscleGroup.CORE], "deadlift_1rm", 0.95, family="deadlift_pattern"),
    Exercise("Dumbbell Deadlift", MuscleGroup.BACK, Equipment.DUMBBELL, True, MovementPattern.HINGE, LiftTier.MAIN, [MuscleGroup.LEGS, MuscleGroup.CORE], "deadlift_1rm", 0.85, family="deadlift_pattern"),
    Exercise("Barbell Row", MuscleGroup.BACK, Equipment.BARBELL, True, MovementPattern.HORIZONTAL_PULL, LiftTier.SECONDARY, [MuscleGroup.ARMS], None, 1.0, family="row_horizontal"),
    Exercise("One-Arm Dumbbell Row", MuscleGroup.BACK, Equipment.DUMBBELL, True, MovementPattern.HORIZONTAL_PULL, LiftTier.SECONDARY, [MuscleGroup.ARMS], None, 1.0, family="row_horizontal"),
    Exercise("Lat Pulldown", MuscleGroup.BACK, Equipment.MACHINE, False, MovementPattern.VERTICAL_PULL, LiftTier.ACCESSORY, [MuscleGroup.ARMS], None, 1.0, family="pull_vertical"),
    Exercise("Pullups", MuscleGroup.BACK, Equipment.BODYWEIGHT, False, MovementPattern.VERTICAL_PULL, LiftTier.SECONDARY, [MuscleGroup.ARMS], None, 1.0, family="pull_vertical"),
    
    # Shoulders
    Exercise("Overhead Press", MuscleGroup.SHOULDERS, Equipment.BARBELL, True, MovementPattern.VERTICAL_PUSH, LiftTier.MAIN, [MuscleGroup.ARMS], "ohp_1rm", 1.0, family="vertical_press"),
    Exercise("Dumbbell Shoulder Press", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, True, MovementPattern.VERTICAL_PUSH, LiftTier.MAIN, [MuscleGroup.ARMS], "ohp_1rm", 0.85, family="vertical_press"),
    Exercise("Lateral Raises", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, False, MovementPattern.SHOULDER_ISO, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Front Raises", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, False, MovementPattern.SHOULDER_ISO, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Rear Delt Flyes", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, False, MovementPattern.SHOULDER_ISO, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Lateral Raises", MuscleGroup.SHOULDERS, Equipment.MACHINE, False, MovementPattern.SHOULDER_ISO, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Rear Delt Flyes", MuscleGroup.SHOULDERS, Equipment.MACHINE, False, MovementPattern.SHOULDER_ISO, LiftTier.ISOLATION, [], None, 1.0),

    # Arms
    Exercise("Dumbbell Bicep Curl", MuscleGroup.ARMS, Equipment.DUMBBELL, False, MovementPattern.ARMS, LiftTier.ISOLATION, [], None, 1.0),
    Exercise("Tricep Pushdown", MuscleGroup.ARMS, Equipment.MACHINE, False, MovementPattern.ARMS, LiftTier.ISOLATION, [], None, 1.0),

    # Core
    Exercise("Plank", MuscleGroup.CORE, Equipment.BODYWEIGHT, False, MovementPattern.CORE, LiftTier.ACCESSORY, [], None, 1.0, family="core"),
    
    # Cardio
    
    Exercise("Outdoor Run", MuscleGroup.CARDIO, Equipment.BODYWEIGHT, False, MovementPattern.CARDIO, LiftTier.CARDIO, [], None, 1.0),
    Exercise("Brisk Walk", MuscleGroup.CARDIO, Equipment.BODYWEIGHT, False, MovementPattern.CARDIO, LiftTier.CARDIO, [], None, 1.0),
    Exercise("Jump Rope", MuscleGroup.CARDIO, Equipment.BODYWEIGHT, False, MovementPattern.CARDIO, LiftTier.CARDIO, [], None, 1.0),
    Exercise("Treadmill Run", MuscleGroup.CARDIO, Equipment.MACHINE, False, MovementPattern.CARDIO, LiftTier.CARDIO, [], None, 1.0),
    Exercise("Cycling", MuscleGroup.CARDIO, Equipment.MACHINE, False, MovementPattern.CARDIO, LiftTier.CARDIO, [], None, 1.0),
]

MUSCLE_GROUPS = [mg for mg in MuscleGroup]

