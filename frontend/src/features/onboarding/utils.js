import { WEEKDAYS } from "./constants";

export function toNumber(v) {
  const n = Number(v);
  return v !== "" && !Number.isNaN(n) ? n : null;
}

export function sortDaysLowercase(days) {
  return [...days]
    .sort((a, b) => WEEKDAYS.indexOf(a) - WEEKDAYS.indexOf(b))
    .map((d) => d.toLowerCase());
}

export function goalToEnum(goalLabel) {
  return goalLabel.toLowerCase().replace(" ", "_");
}

export function durationToMinutes(durationLabel) {
  return parseInt(durationLabel, 10);
}
