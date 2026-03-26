from ortools.sat.python import cp_model

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
)

class InfeasiblePlanError(Exception):
    pass


WEEKDAY_ORDER: dict[Weekday, int] = {
    Weekday.MONDAY: 0,
    Weekday.TUESDAY: 1,
    Weekday.WEDNESDAY: 2,
    Weekday.THURSDAY: 3,
    Weekday.FRIDAY: 4,
    Weekday.SATURDAY: 5,
    Weekday.SUNDAY: 6,
}

# default params
DEFAULT_REP_RANGE = "6-10"
DEFAULT_1RM_PERCENT_RANGE: tuple[float, float] = (0.65, 0.80)

CARDIO_GROUP = MuscleGroup.CARDIO

# Base pattern sets (hinge is separate for split-dependent classification)
PUSH_PAT = {MovementPattern.HORIZONTAL_PUSH, MovementPattern.VERTICAL_PUSH}
PULL_PAT = {MovementPattern.HORIZONTAL_PULL, MovementPattern.VERTICAL_PULL}
LEGS_PAT = {MovementPattern.SQUAT, MovementPattern.SINGLE_LEG}
HINGE_PAT = {MovementPattern.HINGE}

# model would add these fillers so i penelised it for spamming these 
FILLER_PRONE = {"Pushups", "Plank", "Bodyweight Squats"}


class TrainingPlanOptimiser:
    def __init__(self, request: GeneratePlanRequest,weights:dict[str,int]):
        self.request = request
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.num_search_workers = 8
        
        self.solver.parameters.max_time_in_seconds = 10
        self.weights = weights

        self.is_bodyweight_only = set(self.request.equipment) <= {Equipment.BODYWEIGHT}

        allowed_equipment = self.request.equipment | {Equipment.BODYWEIGHT}
        include_cardio = self.request.include_cardio or self.is_bodyweight_only
        self.available_exercises: list[Exercise] = []
        for ex in EXERCISES:
            if ex.equipment not in allowed_equipment:
                continue
            if ex.name in self.request.excluded_exercises:
                continue
            if ex.muscle_group == CARDIO_GROUP and not include_cardio:
                continue
            self.available_exercises.append(ex)

        self.days: list[Weekday] = sorted(
            self.request.available_days, key=lambda d: WEEKDAY_ORDER[d]
        )
      
        self.push_idxs = []
        self.pull_idxs = []
        self.legs_idxs = []
        self.hinge_idxs = []
        self.squat_idxs = []
        self.arms_idxs = []
        self.filler_idxs = []
        #get the indexes of the available exercises for each patter easier to add certain patterns to constraints 
        for i, ex in enumerate(self.available_exercises):
            if ex.pattern in PUSH_PAT:
                self.push_idxs.append(i)
            if ex.pattern in PULL_PAT:
                self.pull_idxs.append(i)
            if ex.pattern in LEGS_PAT:
                self.legs_idxs.append(i)
            if ex.pattern in HINGE_PAT:
                self.hinge_idxs.append(i)
            if ex.pattern == MovementPattern.SQUAT:
                self.squat_idxs.append(i)
            if ex.muscle_group == MuscleGroup.ARMS or ex.pattern == MovementPattern.ARMS:
                self.arms_idxs.append(i)
            if ex.name in FILLER_PRONE:
                self.filler_idxs.append(i)


    def make_split_dict(self) -> dict[Weekday, SplitType]:
        #get a split dictionary based on the number of available days
        n = len(self.days)
        splitDict: dict[Weekday, SplitType] = {}
        
        if n == 1:
            splitDict[self.days[0]] = SplitType.FULL_BODY
        elif n == 2:
            splitDict[self.days[0]] = SplitType.UPPER
            splitDict[self.days[1]] = SplitType.LOWER
        elif n == 3:
            # PPL
            splitDict[self.days[0]] = SplitType.PUSH
            splitDict[self.days[1]] = SplitType.PULL
            splitDict[self.days[2]] = SplitType.LEGS
        elif n == 4:
            # Upper/Lower x2
            splitDict[self.days[0]] = SplitType.UPPER
            splitDict[self.days[1]] = SplitType.LOWER
            splitDict[self.days[2]] = SplitType.UPPER
            splitDict[self.days[3]] = SplitType.LOWER
        elif n == 5:
            # PPL + Upper + Lower
            splitDict[self.days[0]] = SplitType.PUSH
            splitDict[self.days[1]] = SplitType.PULL
            splitDict[self.days[2]] = SplitType.LEGS
            splitDict[self.days[3]] = SplitType.UPPER
            splitDict[self.days[4]] = SplitType.LOWER
        elif n == 6:
            # PPL x2
            splitDict[self.days[0]] = SplitType.PUSH
            splitDict[self.days[1]] = SplitType.PULL
            splitDict[self.days[2]] = SplitType.LEGS
            splitDict[self.days[3]] = SplitType.PUSH
            splitDict[self.days[4]] = SplitType.PULL
            splitDict[self.days[5]] = SplitType.LEGS
        else:
            # 7 days: PPL x2 + Full Body
            splitDict[self.days[0]] = SplitType.PUSH
            splitDict[self.days[1]] = SplitType.PULL
            splitDict[self.days[2]] = SplitType.LEGS
            splitDict[self.days[3]] = SplitType.PUSH
            splitDict[self.days[4]] = SplitType.PULL
            splitDict[self.days[5]] = SplitType.LEGS
            splitDict[self.days[6]] = SplitType.FULL_BODY
        
        return splitDict

    def get_split_type(self, split_dict: dict[Weekday, SplitType]) -> str:
        #get the split type based on the split dictionary this to do with how im treating hinge exercises in certain splits
        roles = set(split_dict.values())
        has_ppl = bool(roles & {SplitType.PUSH, SplitType.PULL, SplitType.LEGS})
        has_ul = bool(roles & {SplitType.UPPER, SplitType.LOWER})
        if has_ppl and has_ul:
            return "mixed"
        if has_ppl:
            return "ppl"
        if has_ul:
            return "upper_lower"
        return "full_body"

    def get_role_patterns(self, role: SplitType, split_type: str) -> set[MovementPattern]:
        #get the patterns eg push = hor push and ver push based on the split type 
        #this also depends on how i classify hinge exercises in certain splits
        #used for role purity constraints 
        if role == SplitType.PUSH:
            return PUSH_PAT | {MovementPattern.SHOULDER_ISO}
        elif role == SplitType.PULL:
            # PPL/mixed: hinge counts as pull
            return PULL_PAT | HINGE_PAT if split_type in ("ppl", "mixed") else PULL_PAT
        elif role == SplitType.LEGS:
            # PPL: legs is squat-dominant (no hinge)
            return LEGS_PAT
        elif role == SplitType.UPPER:
            return PUSH_PAT | PULL_PAT | {MovementPattern.SHOULDER_ISO}
        elif role == SplitType.LOWER:
            # upper_lower: hinge counts as lower
            if split_type == "upper_lower":
                return LEGS_PAT | HINGE_PAT
            
            return LEGS_PAT
        elif role == SplitType.FULL_BODY:
            return PUSH_PAT | PULL_PAT | LEGS_PAT | HINGE_PAT | {MovementPattern.SHOULDER_ISO}
        return set()

    def get_role_idxs(self, role: SplitType, split_type: str) -> list[int]:
        #gets the indexs of ex that match the patter for the role eg [0, 1, 4] for push role
        patterns = self.get_role_patterns(role, split_type)
        role_idxs = []
        for i,ex in enumerate(self.available_exercises):
            if ex.pattern in patterns:
                role_idxs.append(i)

        return role_idxs

    def check_split_feasibility(self, split_dict: dict[Weekday, SplitType], split_type: str) -> None:

        for day, role in split_dict.items():
            role_idxs = self.get_role_idxs(role, split_type)
            if len(role_idxs) == 0:
                raise InfeasiblePlanError(f"No exercises available for {role.value} day with chosen equipment/exclusions")
            
            # Check MAIN lifts exist for role (all goals).
            # We require at least one MAIN per day in the solver
            if not self.is_bodyweight_only:
                patterns = self.get_role_patterns(role, split_type)
                main_role_idxs = [
                    i
                    for i, ex in enumerate(self.available_exercises)
                    if ex.tier == LiftTier.MAIN and ex.pattern in patterns
                ]
                if not main_role_idxs:
                    raise InfeasiblePlanError(f"No MAIN lift available for {role.value} day with chosen equipment/exclusions")

    def get_exercise_params(
        self, ex: Exercise
    ) -> tuple[str, tuple[float, float] | None, int, int, int, int]:
        #exercise time is: sets * work_minutes + (sets - 1) * rest_minutes
       
        
        rep_range = DEFAULT_REP_RANGE
        one_rpm_per: tuple[float, float] | None = DEFAULT_1RM_PERCENT_RANGE

        # core exercises g
        if ex.muscle_group == MuscleGroup.CORE or ex.pattern == MovementPattern.CORE:
            rep_range = "30-60s"
            one_rpm_per = None
            min_sets, max_sets = 2, 4
            work_minutes = 2
            rest_minutes = 1
            return rep_range, one_rpm_per, min_sets, max_sets, work_minutes, rest_minutes

        if ex.muscle_group == CARDIO_GROUP:
            rep_range = "15 Minutes"
            one_rpm_per = None
            min_sets, max_sets = 1, 1
            work_minutes = 15
            rest_minutes = 0
            return rep_range, one_rpm_per, min_sets, max_sets, work_minutes, rest_minutes

        # params based off the goal (strength, hypertrophy, fat loss, general fitness) and lift tier 
        if self.request.training_goal == TrainingGoal.STRENGTH:
            if ex.tier == LiftTier.MAIN:
                rep_range = "2-5"
                one_rpm_per = (0.75, 0.82)
                min_sets, max_sets = 3, 5
                work_minutes = 2
                rest_minutes = 4
            elif ex.tier == LiftTier.SECONDARY:
                rep_range = "3-5"
                one_rpm_per = (0.70, 0.80)
                min_sets, max_sets = 3, 4
                work_minutes = 2
                rest_minutes = 3
            elif ex.tier == LiftTier.ACCESSORY:
                rep_range = "8-12"
                one_rpm_per = (0.6, 0.7)
                min_sets, max_sets = 2, 4
                work_minutes = 2
                rest_minutes = 2
            elif ex.tier == LiftTier.ISOLATION:
                rep_range = "10-15"
                one_rpm_per = (0.5, 0.65)
                min_sets, max_sets = 2, 3
                work_minutes = 1
                rest_minutes = 1
            else:
                rep_range = "10-15"
                one_rpm_per = None
                min_sets, max_sets = 1, 1
                work_minutes = 1
                rest_minutes = 0
        elif self.request.training_goal == TrainingGoal.HYPERTROPHY:
            rep_range = "6-10"
            one_rpm_per = (0.65, 0.78)
            if ex.tier == LiftTier.MAIN:
                min_sets, max_sets = 3, 5
                work_minutes = 2
                rest_minutes = 3
            elif ex.tier == LiftTier.SECONDARY:
                min_sets, max_sets = 4, 5
                work_minutes = 2
                rest_minutes = 2
            elif ex.tier == LiftTier.ACCESSORY:
                min_sets, max_sets = 4, 5
                work_minutes = 2
                rest_minutes = 2
            else:
                min_sets, max_sets = 2, 3
                work_minutes = 1
                rest_minutes = 1
        elif self.request.training_goal == TrainingGoal.FAT_LOSS:
            rep_range = "10-15"
            one_rpm_per = (0.5, 0.65)
            min_sets, max_sets = 2, 3
            work_minutes = 1
            rest_minutes = 1
        else:
            # GENERAL_FITNESS
            rep_range = "6-10"
            one_rpm_per = (0.65, 0.75)
            min_sets, max_sets = 2, 4
            work_minutes = 1 if ex.tier in (LiftTier.ACCESSORY, LiftTier.ISOLATION) else 2
            rest_minutes = 1 if ex.tier in (LiftTier.ACCESSORY, LiftTier.ISOLATION) else 2

        return rep_range, one_rpm_per, min_sets, max_sets, work_minutes, rest_minutes

    def solve(self) -> GeneratePlanResponse:
        #  Split  & feasibility checks 
        split_dict = self.make_split_dict()
        split_type = self.get_split_type(split_dict)
        self.check_split_feasibility(split_dict, split_type)

        #x is a dict  which is 1 if the ex is on that dady 0 if not
        x: dict[tuple[Weekday, int], cp_model.IntVar] = {}
        #populate the x dict with bool vars for eacg day ex pair 
        for day in self.days:
            for i in range(len(self.available_exercises)):
                x[(day, i)] = self.model.NewBoolVar(f"x_{day}_{i}")

        ex_params: dict[int, tuple[
            str, #rep range
            tuple[float, float] | None, #1rm percent range
            int, #min sets
            int, #max sets
            int, #work minutes
            int, #rest minutes
            ]] = {} 
        for i, ex in enumerate(self.available_exercises):
            ex_params[i] = self.get_exercise_params(ex)

        sets: dict[tuple[Weekday, int], cp_model.IntVar] = {}
        for day in self.days:#pop sets dict with int vars 0 or inbetween min and max sets 
            for i in range(len(self.available_exercises)):
                _, _, min_sets, max_sets, _, _ = ex_params[i]
                s = self.model.NewIntVar(0, max_sets, f"sets_{day}_{i}")
                sets[(day, i)] = s
                self.model.Add(s <= max_sets * x[(day, i)])
                self.model.Add(s >= min_sets * x[(day, i)])

        
        # session time cap: sets*work + (sets-x)*rest  (rest after last set not counted)
        if self.request.training_goal == TrainingGoal.GENERAL_FITNESS:
            min_time = self.request.session_duration_minutes // 2
        else:
            min_time = (2 * self.request.session_duration_minutes) // 3   # had an issue where it was getting short sessions
        for day in self.days:
            total_time=0
            for i in range(len(self.available_exercises)):
                work_time = ex_params[i][4]
                rest_time =  ex_params[i][5]

                s=sets[(day, i)]
                chosen = x[(day, i)]
                total_time += work_time * s + rest_time * (s - chosen)
                
                
            self.model.Add(total_time <= self.request.session_duration_minutes)
            self.model.Add(total_time >= min_time)

        # each day must have at least one exercise
        # for day in self.days: might bring back if i add a deload 
        #    self.model.Add(sum(x[(day, i)] for i in range(len(self.available_exercises))) >= 1) 

        # MAIN lifts per day: 1-2
        all_main_idxs = [i for i, ex in enumerate(self.available_exercises) if ex.tier == LiftTier.MAIN]
        if not self.is_bodyweight_only:
            for day in self.days:
                self.model.Add(sum(x[(day, i)] for i in all_main_idxs) >= 1)
                self.model.Add(sum(x[(day, i)] for i in all_main_idxs) <= 2)

        # prevent duplicate MAIN movement patterns per day (MAIN tier only)
        for day in self.days:
            for pat in MovementPattern:
                pat_main_idxs = []
                for i in all_main_idxs:
                    if self.available_exercises[i].pattern == pat:
                        pat_main_idxs.append(i)
                if pat_main_idxs:
                    self.model.Add(sum(x[(day, i)] for i in pat_main_idxs) <= 1)

        # family uniqueness (per day): at most one exercise from each family
    
        family_to_idxs: dict[str, list[int]] = {}
        for i, ex in enumerate(self.available_exercises):
            if ex.tier not in (LiftTier.MAIN, LiftTier.SECONDARY, LiftTier.ACCESSORY):
                continue
            fam = getattr(ex, "family", None)
            if not fam:
                continue
            family_to_idxs.setdefault(fam, []).append(i)

        for day in self.days:
            for fam, idxs in family_to_idxs.items():
                if len(idxs) <= 1:
                    continue
                self.model.Add(sum(x[(day, i)] for i in idxs) <= 1)

        #split-based constraints 
        # bans offrole ex   
        always_allowed_patterns = {MovementPattern.ARMS, MovementPattern.CORE, MovementPattern.CARDIO}
        always_allowed_muscles = {MuscleGroup.ARMS, MuscleGroup.CORE, MuscleGroup.CARDIO}
        for day in self.days:
            role = split_dict[day]
            if role == SplitType.FULL_BODY:
                continue
            allowed_role_patterns = self.get_role_patterns(role, split_type)
            for i, ex in enumerate(self.available_exercises):
                if (
                    ex.pattern not in allowed_role_patterns
                    and ex.pattern not in always_allowed_patterns
                    and ex.muscle_group not in always_allowed_muscles
                ):
                    self.model.Add(x[(day, i)] == 0)

        # split-based constraints
        for day in self.days:
            role = split_dict[day]
            role_patterns = self.get_role_patterns(role, split_type)
            role_idxs = self.get_role_idxs(role, split_type)

            # must have at least one on-role exercise
            if role_idxs:
                self.model.Add(sum(x[(day, i)] for i in role_idxs) >= 1)
            

            #to stop isolation only days 
            if self.request.training_goal != TrainingGoal.STRENGTH:
                push_non_iso = []
                pull_non_iso = []
                hinge_non_iso = []
                legs_non_iso = []
                for i, ex in enumerate(self.available_exercises):
                    if ex.tier == LiftTier.ISOLATION:
                        continue
                    if ex.pattern in PUSH_PAT:
                        push_non_iso.append(i)
                    if ex.pattern in PULL_PAT:
                        pull_non_iso.append(i)
                    if ex.pattern in HINGE_PAT:
                        hinge_non_iso.append(i)
                    if ex.pattern in LEGS_PAT:
                        legs_non_iso.append(i)

                if role == SplitType.PUSH:
                    if push_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in push_non_iso) >= 1)
                elif role == SplitType.PULL:#pull days also have hinge ex
                    role_non_iso = []
                    for i, ex in enumerate(self.available_exercises):
                        if ex.tier != LiftTier.ISOLATION and ex.pattern in role_patterns:
                            role_non_iso.append(i)
                    if role_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in role_non_iso) >= 1)
                elif role == SplitType.LEGS:
                    if legs_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in legs_non_iso) >= 1)
                elif role == SplitType.UPPER:
                    if push_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in push_non_iso) >= 1)
                    if pull_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in pull_non_iso) >= 1)
                elif role == SplitType.LOWER:
                    if legs_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in legs_non_iso) >= 1)
                    if MovementPattern.HINGE in role_patterns and hinge_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in hinge_non_iso) >= 1)
                elif role == SplitType.FULL_BODY:
                    if push_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in push_non_iso) >= 1)
                    if pull_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in pull_non_iso) >= 1)
                    legs_hinge_non_iso = legs_non_iso + hinge_non_iso
                    if legs_hinge_non_iso:
                        self.model.Add(sum(x[(day, i)] for i in legs_hinge_non_iso) >= 1)

            # FULL_BODY push/pull/legs have at least one of each
            if role == SplitType.FULL_BODY:
                push_idxs = []
                pull_idxs = []
                legs_hinge_idxs = []
                for i, ex in enumerate(self.available_exercises):
                    if ex.pattern in PUSH_PAT:
                        push_idxs.append(i)
                    if ex.pattern in PULL_PAT:
                        pull_idxs.append(i)
                    if ex.pattern in (LEGS_PAT | HINGE_PAT):
                        legs_hinge_idxs.append(i)
                if push_idxs:
                    self.model.Add(sum(x[(day, i)] for i in push_idxs) >= 1)
                if pull_idxs:
                    self.model.Add(sum(x[(day, i)] for i in pull_idxs) >= 1)
                if legs_hinge_idxs:
                    self.model.Add(sum(x[(day, i)] for i in legs_hinge_idxs) >= 1)

            # UPPER push + pull presence + push/pull balance
            elif role == SplitType.UPPER:
                push_idxs = []
                pull_idxs = []
                for i, ex in enumerate(self.available_exercises):
                    if ex.pattern in PUSH_PAT:
                        push_idxs.append(i)
                    if ex.pattern in PULL_PAT:
                        pull_idxs.append(i)
                if push_idxs:
                    self.model.Add(sum(x[(day, i)] for i in push_idxs) >= 1)
                if pull_idxs:
                    self.model.Add(sum(x[(day, i)] for i in pull_idxs) >= 1)

                if push_idxs and pull_idxs:
                    push_count = sum(x[(day, i)] for i in push_idxs)
                    pull_count = sum(x[(day, i)] for i in pull_idxs)
                    self.model.Add(push_count - pull_count <= 1)
                    self.model.Add(pull_count - push_count >= -1)
                    
                  

            # LOWER squat/hinge 
            elif role == SplitType.LOWER:
                squat_non_iso_idxs = []
                for i, ex in enumerate(self.available_exercises):
                    if ex.pattern == MovementPattern.SQUAT and ex.tier != LiftTier.ISOLATION:
                        squat_non_iso_idxs.append(i)
                if squat_non_iso_idxs and MovementPattern.HINGE in role_patterns and self.hinge_idxs:
                    self.model.Add(sum(x[(day, i)] for i in squat_non_iso_idxs) >= 1)
                    self.model.Add(sum(x[(day, i)] for i in self.hinge_idxs) >= 1)

        # have at least one decent horiz push on push/upper days 
        if self.request.training_goal == TrainingGoal.STRENGTH:
            horiz_push_idxs = []
            for i, ex in enumerate(self.available_exercises):
                if ex.pattern == MovementPattern.HORIZONTAL_PUSH and ex.tier in (LiftTier.MAIN, LiftTier.SECONDARY):
                    horiz_push_idxs.append(i)
            if horiz_push_idxs:
                for day in self.days:
                    if split_dict.get(day) in (SplitType.PUSH, SplitType.UPPER):
                        self.model.Add(sum(x[(day, i)] for i in horiz_push_idxs) >= 1)

        # lock accessory ex to a decent lift of the same group  
        chest_main = []
        chest_acc = []
        shoulders_main = []
        shoulders_acc = []
        for i, ex in enumerate(self.available_exercises):
            if ex.muscle_group == MuscleGroup.CHEST and ex.tier in (LiftTier.MAIN, LiftTier.SECONDARY):
                chest_main.append(i)
            if ex.muscle_group == MuscleGroup.CHEST and ex.tier in (LiftTier.ACCESSORY, LiftTier.ISOLATION):
                chest_acc.append(i)
            if ex.muscle_group == MuscleGroup.SHOULDERS and ex.tier in (LiftTier.MAIN, LiftTier.SECONDARY):
                shoulders_main.append(i)
            if ex.muscle_group == MuscleGroup.SHOULDERS and ex.tier in (LiftTier.ACCESSORY, LiftTier.ISOLATION):
                shoulders_acc.append(i)

        if chest_main and chest_acc:

            for day in self.days:
                chest_acc_count = sum(x[(day, i)] for i in chest_acc)
                chest_main_count = sum(x[(day, i)] for i in chest_main)

                self.model.Add(chest_acc_count <= len(chest_acc) * chest_main_count)

        if shoulders_main and shoulders_acc:
            for day in self.days:
                shoulders_acc_count = sum(x[(day, i)] for i in shoulders_acc)
                shoulders_main_count = sum(x[(day, i)] for i in shoulders_main)

                self.model.Add(shoulders_acc_count <= len(shoulders_acc) * shoulders_main_count)
    
        # === Cross-day structure constraints ===
        
        always_allowed_idxs = []
        for i,ex in enumerate(self.available_exercises):
            if ex.pattern in always_allowed_patterns or ex.muscle_group in always_allowed_muscles:
                always_allowed_idxs.append(i)
            
        for day, next_day in zip(self.days, self.days[1:]):
            for i in always_allowed_idxs:
                if self.is_bodyweight_only and self.available_exercises[i].muscle_group == CARDIO_GROUP:
                    continue
                self.model.Add(x[(day, i)] + x[(next_day, i)] <= 1)

        

        # FULL_BODY 
        full_body=[d for d in self.days if split_dict.get(d) == SplitType.FULL_BODY]

        if full_body:
            squat_1rm_idxs = []
            deadlift_1rm_idxs = []
            for i, ex in enumerate(self.available_exercises):
                if ex.primary_1rm_link == "squat_1rm":
                    squat_1rm_idxs.append(i)
                if ex.primary_1rm_link == "deadlift_1rm":
                    deadlift_1rm_idxs.append(i)

            if squat_1rm_idxs and deadlift_1rm_idxs:
                squat_count = sum(x[(day, i)] for i in squat_1rm_idxs)
                deadlift_count = sum(x[(day, i)] for i in deadlift_1rm_idxs)
                self.model.Add(squat_count + deadlift_count <= 1)

        
        if self.request.training_goal == TrainingGoal.FAT_LOSS:
            per_muscle_cap=3
        elif self.request.training_goal != TrainingGoal.STRENGTH:
            per_muscle_cap = 2 if self.request.session_duration_minutes <= 60 else 3

        if self.request.training_goal != TrainingGoal.STRENGTH:
            for day in self.days:
                for mg in MuscleGroup:
                    if mg == CARDIO_GROUP:
                        continue
                    idxs = []
                    for i, ex in enumerate(self.available_exercises):
                        if ex.muscle_group == mg:
                            idxs.append(i)
                    if idxs:
                        self.model.Add(sum(x[(day, i)] for i in idxs) <= per_muscle_cap)
        else:
            for day in self.days:
                for mg in MuscleGroup:
                    if mg == CARDIO_GROUP:
                        continue
                    iso_idxs = []
                    for i, ex in enumerate(self.available_exercises):
                        if ex.muscle_group == mg and ex.tier == LiftTier.ISOLATION:
                            iso_idxs.append(i)
                    if iso_idxs:
                        self.model.Add(sum(x[(day, i)] for i in iso_idxs) <= 1)

        # filler-prone hard weekly cap 
        if self.filler_idxs and not self.is_bodyweight_only:
            for i in self.filler_idxs:
                self.model.Add(sum(x[(day, i)] for day in self.days) <= 1)

        # add required primary lifts
        for req in self.request.required_primary_lifts:
            req_idxs = []
            for i, ex in enumerate(self.available_exercises):
                if ex.primary_1rm_link == req.value:
                    req_idxs.append(i)
            if req_idxs:
                self.model.Add(sum(x[(day, i)] for day in self.days for i in req_idxs) >= 1)

        #scoreboard to penalise being under/over weekly volume 
       
        primary_sets_2x: dict[tuple[Weekday, MuscleGroup], cp_model.IntVar] = {}
        secondary_sets_2x: dict[tuple[Weekday, MuscleGroup], cp_model.IntVar] = {}
        total_sets_2x: dict[tuple[Weekday, MuscleGroup], cp_model.IntVar] = {}
        major_mgs = [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.LEGS, MuscleGroup.SHOULDERS]

        for day in self.days:
            for mg in major_mgs:
                p = self.model.NewIntVar(0, 10000, f"p2x_{day}_{mg}")
                s = self.model.NewIntVar(0, 10000, f"s2x_{day}_{mg}")
                t = self.model.NewIntVar(0, 10000, f"t2x_{day}_{mg}")
                primary_sets_2x[(day, mg)] = p
                secondary_sets_2x[(day, mg)] = s
                total_sets_2x[(day, mg)] = t

                self.model.Add(
                    p
                    == sum(
                        2 * sets[(day, i)]
                        for i, ex in enumerate(self.available_exercises)
                        if ex.muscle_group == mg
                    )
                )
                self.model.Add(
                    s
                    == sum(
                        sets[(day, i)]
                        for i, ex in enumerate(self.available_exercises)
                        if mg in ex.secondary_muscles
                    )
                )
                self.model.Add(t == p + s)

        weekly_sets_2x: dict[MuscleGroup, cp_model.IntVar] = {}
        weekly_under: dict[MuscleGroup, cp_model.IntVar] = {}
        weekly_over: dict[MuscleGroup, cp_model.IntVar] = {}
        weekly_band_actual = {
            MuscleGroup.CHEST: (12, 22),
            MuscleGroup.BACK: (12, 22),
            MuscleGroup.LEGS: (12, 26),
            MuscleGroup.SHOULDERS: (6, 16),
        }
        for mg in major_mgs:
            w = self.model.NewIntVar(0, 50000, f"weekly_credits_{mg}")
            weekly_sets_2x[mg] = w
            self.model.Add(w == sum(total_sets_2x[(day, mg)] for day in self.days))
            if any(ex.muscle_group == mg or mg in ex.secondary_muscles for ex in self.available_exercises):
                low, high = weekly_band_actual[mg]
                low_scaled = low * 2
                high_scaled = high * 2
                under = self.model.NewIntVar(0, low_scaled, f"under_{mg}")
                over = self.model.NewIntVar(0, 50000, f"over_{mg}")
                weekly_under[mg] = under
                weekly_over[mg] = over
                self.model.Add(w + under >= low_scaled)
                self.model.Add(w - over <= high_scaled)

       
        
        
        def ex_weight(ex: Exercise) -> int:
            if self.request.training_goal == TrainingGoal.STRENGTH:
                if ex.tier == LiftTier.MAIN:
                    return 8
                if ex.tier == LiftTier.SECONDARY:
                    return 5
                if ex.tier == LiftTier.ACCESSORY:
                    return 3
                if ex.tier == LiftTier.ISOLATION:
                    return 2
                return 1
            if self.request.training_goal == TrainingGoal.HYPERTROPHY:
                if ex.tier == LiftTier.MAIN:
                    return 5
                if ex.tier == LiftTier.SECONDARY:
                    return 4
                if ex.tier == LiftTier.ACCESSORY:
                    return 3
                if ex.tier == LiftTier.ISOLATION:
                    return 3
                return 1
            if self.request.training_goal == TrainingGoal.FAT_LOSS:
                if ex.muscle_group == CARDIO_GROUP:
                    return 5
                return 2
            if self.request.training_goal == TrainingGoal.GENERAL_FITNESS:
                return 2
            return 1


        # perfer plans the give more weighted exercises 
        stimulus_scale = self.weights["stimulus_scale"]
        stimulus_sum=0
        for day in self.days:
            for i ,ex in enumerate(self.available_exercises):
                w=ex_weight(ex)
                stimulus_sum += w * sets[(day, i)]
        stimulus_term = stimulus_scale * stimulus_sum
        

        # arms bonus
        arms_bonus = self.weights["arms_bonus"]*len(self.days)
        arms_present = self.model.NewBoolVar("arms_present")
        if self.arms_idxs:
            self.model.Add(
                sum(x[(day, i)] for day in self.days for i in self.arms_idxs) >= 1
            ).OnlyEnforceIf(arms_present)
            self.model.Add(
                sum(x[(day, i)] for day in self.days for i in self.arms_idxs) == 0
            ).OnlyEnforceIf(arms_present.Not())
        else:
            self.model.Add(arms_present == 0)

       
        # weekly set penalty 
        under_penalty = self.weights["under_penalty"]
        over_penalty = self.weights["over_penalty"]
        band_penalty = (
            under_penalty * sum(weekly_under.values())
            + over_penalty * sum(weekly_over.values())
        )

        

        # repetition penalties (base + filler)
        week_count: dict[int, cp_model.IntVar] = {}
        repeat_vars: dict[int, cp_model.IntVar] = {}
        for i, ex in enumerate(self.available_exercises):
            wc = self.model.NewIntVar(0, len(self.days), f"week_count_{i}")
            week_count[i] = wc
            self.model.Add(wc == sum(x[(day, i)] for day in self.days))
            rep = self.model.NewIntVar(0, len(self.days), f"repeat_{i}")
            repeat_vars[i] = rep
            self.model.Add(rep >= wc - 1)
            self.model.Add(rep >= 0)
        
        # favor variance ex in longer weeks
        #base_repeat_penalty = 3 if len(self.days) <= 3 else 8  
        base_repeat_penalty = self.weights["base_repeat_penalty"]
        repeat_penalty_total = base_repeat_penalty * sum(
            repeat_vars[i] for i in range(len(self.available_exercises))
        )

        # filler base penalty
        filler_base_penalty_k = self.weights["filler_base_penalty"]
        filler_selected = sum(
            x[(day, i)]
            for day in self.days
            for i in self.filler_idxs
        ) if self.filler_idxs else 0

       

        objective_expr = (
            stimulus_term
            + arms_bonus * arms_present
            - band_penalty
            - repeat_penalty_total
            - filler_base_penalty_k * filler_selected
            
        )
        self.model.Maximize(objective_expr)

        # === Solve & format output ===
        status = self.solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise InfeasiblePlanError("Unable to generate a feasible training plan.")

        # solver -> week_plan
        week_plan: dict[Weekday, list[ExercisePlan]] = {}
        for day in self.days:
            exercises_for_day: list[ExercisePlan] = []
            for i, ex in enumerate(self.available_exercises):
                if self.solver.Value(x[(day, i)]):
                    exercises_for_day.append(
                        self._format_exercise(
                            ex,
                            int(self.solver.Value(sets[(day, i)])),
                        )
                    )
            week_plan[day] = exercises_for_day

        return GeneratePlanResponse(
            training_goal=self.request.training_goal,
            inferred_split=split_dict,
            week_plan=week_plan,
        )

    def _format_exercise(self, ex: Exercise, sets: int) -> ExercisePlan:
        rep_range, one_rpm_per, _, _, work_minutes, rest_minutes = self.get_exercise_params(ex)

        
        weight_range = None
        weight_display = None
        if ex.muscle_group != CARDIO_GROUP and ex.primary_1rm_link and one_rpm_per is not None:
            one_rm_value = getattr(self.request.one_rep_maxes, ex.primary_1rm_link)
            low_pct, high_pct = one_rpm_per

            min_weight = one_rm_value * low_pct * ex.weight_multiplier
            max_weight = one_rm_value * high_pct * ex.weight_multiplier

            # Dumbbell convention:
            if ex.equipment == Equipment.DUMBBELL:
                per_db_min = float(round(min_weight / 2))
                per_db_max = float(round(max_weight / 2))
                weight_range = WeightRangeKg(min=per_db_min, max=per_db_max)
                if per_db_min == per_db_max:
                    weight_display = f"{int(per_db_min)} kg per dumbbell "
                else:
                    weight_display = f"{int(per_db_min)}-{int(per_db_max)} kg per dumbbell "
            else:
                weight_range = WeightRangeKg(
                    min=float(round(min_weight)),
                    max=float(round(max_weight)),
                )

        return ExercisePlan(
            name=ex.name,
            muscle_group=ex.muscle_group,
            equipment=ex.equipment,
            rep_range=rep_range,
            sets=sets,
            work_minutes=work_minutes,
            rest_minutes=rest_minutes,
            weight_range_kg=weight_range,
            weight_display=weight_display,
        )
