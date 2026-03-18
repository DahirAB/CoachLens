import { DURATIONS, EQUIPMENT, GOALS, WEEKDAYS } from "./constants";

const GOAL_BY_ENUM = new Map(
  GOALS.map((goal) => [goal.toLowerCase().replace(" ", "_"), goal]),
);

const EQUIPMENT_BY_ENUM = new Map(
  EQUIPMENT.map((item) => [item.toLowerCase(), item]),
);

const DAY_BY_ENUM = new Map(
  WEEKDAYS.map((day) => [day.toLowerCase(), day]),
);

export function profileToFormState(profile) {
  const trainingGoal = profile?.training_goal ?? "";
  const availableDays = Array.isArray(profile?.available_days) ? profile.available_days : [];
  const equipment = Array.isArray(profile?.equipment) ? profile.equipment : [];
  const requiredPrimaryLifts = Array.isArray(profile?.required_primary_lifts) ? profile.required_primary_lifts : [];
  const excludedExercises = Array.isArray(profile?.excluded_exercises) ? profile.excluded_exercises : [];

  const durationMinutes = Number(profile?.session_duration_min);
  const durationLabel = Number.isFinite(durationMinutes) ? `${durationMinutes} min` : "";
  const safeDuration = DURATIONS.includes(durationLabel) ? durationLabel : "";

  const toInput = (value) => {
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? String(n) : "";
  };

  return {
    selectedDays: availableDays.map((day) => DAY_BY_ENUM.get(day) ?? day),
    duration: safeDuration,
    goal: GOAL_BY_ENUM.get(trainingGoal) ?? "",
    selectedEquipment: equipment.map((item) => EQUIPMENT_BY_ENUM.get(item) ?? item),
    oneRepMaxes: {
      squat: toInput(profile?.squat_1rm),
      bench: toInput(profile?.bench_1rm),
      deadlift: toInput(profile?.deadlift_1rm),
      ohp: toInput(profile?.ohp_1rm),
    },
    includeCardio: Boolean(profile?.include_cardio),
    requiredPrimaryLifts: [...requiredPrimaryLifts],
    excludedExercises: [...excludedExercises],
  };
}
