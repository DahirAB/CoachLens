const WEEKDAY_ORDER = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

function sortDays(days) {
  return [...days].sort((a, b) => WEEKDAY_ORDER.indexOf(a) - WEEKDAY_ORDER.indexOf(b));
}

function sorted(values) {
  return [...values].sort();
}

function sameArray(left, right) {
  if (left.length !== right.length) return false;
  return left.every((item, index) => item === right[index]);
}

export function hasConstraintsDrift(plan, profile) {
  if (!plan?.request_json || !profile) return false;

  const request = plan.request_json;

  const requestDays = sortDays(Array.isArray(request.available_days) ? request.available_days : []);
  const profileDays = sortDays(Array.isArray(profile.available_days) ? profile.available_days : []);
  if (!sameArray(requestDays, profileDays)) return true;

  const requestEquipment = sorted(Array.isArray(request.equipment) ? request.equipment : []);
  const profileEquipment = sorted(Array.isArray(profile.equipment) ? profile.equipment : []);
  if (!sameArray(requestEquipment, profileEquipment)) return true;

  const requestRequired = sorted(Array.isArray(request.required_primary_lifts) ? request.required_primary_lifts : []);
  const profileRequired = sorted(Array.isArray(profile.required_primary_lifts) ? profile.required_primary_lifts : []);
  if (!sameArray(requestRequired, profileRequired)) return true;

  const requestExcluded = sorted(Array.isArray(request.excluded_exercises) ? request.excluded_exercises : []);
  const profileExcluded = sorted(Array.isArray(profile.excluded_exercises) ? profile.excluded_exercises : []);
  if (!sameArray(requestExcluded, profileExcluded)) return true;

  if ((request.training_goal ?? "") !== (profile.training_goal ?? "")) return true;
  if (Number(request.session_duration_minutes ?? 0) !== Number(profile.session_duration_min ?? 0)) return true;
  if (Boolean(request.include_cardio) !== Boolean(profile.include_cardio)) return true;

  const oneRepMaxes = request.one_rep_maxes ?? {};
  if (Number(oneRepMaxes.squat_1rm ?? 0) !== Number(profile.squat_1rm ?? 0)) return true;
  if (Number(oneRepMaxes.bench_1rm ?? 0) !== Number(profile.bench_1rm ?? 0)) return true;
  if (Number(oneRepMaxes.deadlift_1rm ?? 0) !== Number(profile.deadlift_1rm ?? 0)) return true;
  if (Number(oneRepMaxes.ohp_1rm ?? 0) !== Number(profile.ohp_1rm ?? 0)) return true;

  return false;
}
