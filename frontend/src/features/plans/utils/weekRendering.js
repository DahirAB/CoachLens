export const WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

export function buildRenderDays(weekPlan) {
  if (!weekPlan || typeof weekPlan !== "object") return [];
  const workoutDays = WEEK.filter((d) => Array.isArray(weekPlan[d]) && weekPlan[d].length > 0);
  if (workoutDays.length === 0) return [];
  const firstIdx = WEEK.indexOf(workoutDays[0]);
  const lastIdx = WEEK.indexOf(workoutDays[workoutDays.length - 1]);
  const result = [];
  for (let i = firstIdx; i <= lastIdx; i++) {
    const day = WEEK[i];
    const exercises = weekPlan[day];
    if (Array.isArray(exercises) && exercises.length > 0) {
      result.push({ type: "workout", day, exercises });
    } else {
      result.push({ type: "rest", day });
    }
  }
  return result;
}
//util func done by ai 