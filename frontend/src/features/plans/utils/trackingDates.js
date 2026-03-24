import { WEEK } from "./weekRendering";

export function dateToWeekday(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  const dayNum = d.getDay();
  const weekIdx = dayNum === 0 ? 6 : dayNum - 1;
  return WEEK[weekIdx];
}

export function capitalizeWeekday(dateStr) {
  return dateToWeekday(dateStr).charAt(0).toUpperCase() + dateToWeekday(dateStr).slice(1);
}

export function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

/** First date matching weekday that is on or after the reference date (plan creation). */
export function firstDateForWeekdayOnOrAfter(weekday, referenceDateStr) {
  const refDate = new Date(referenceDateStr + "T12:00:00");
  const targetIdx = WEEK.indexOf(weekday);
  if (targetIdx === -1) return todayStr();
  for (let i = 0; i <= 6; i++) {
    const d = new Date(refDate);
    d.setDate(d.getDate() + i);
    const dIdx = d.getDay() === 0 ? 6 : d.getDay() - 1;
    if (dIdx === targetIdx) return d.toISOString().slice(0, 10);
  }
  return todayStr();
}

/**
 * Resolve the calendar date for `weekday` within the training week anchored
 * by the earliest workout day on or after `referenceDateStr`.
 */
export function resolvedDateForDay(weekday, allWorkoutDays, referenceDateStr) {
  if (!referenceDateStr || !allWorkoutDays || allWorkoutDays.length === 0) {
    return todayStr();
  }

  const sorted = [...allWorkoutDays].sort(
    (a, b) => WEEK.indexOf(a) - WEEK.indexOf(b),
  );
  const earliestDay = sorted[0];

  const anchorDateStr = firstDateForWeekdayOnOrAfter(earliestDay, referenceDateStr);
  const anchor = new Date(anchorDateStr + "T12:00:00");

  const anchorWeekIdx = WEEK.indexOf(earliestDay);
  const monday = new Date(anchor);
  monday.setDate(monday.getDate() - anchorWeekIdx);

  const targetIdx = WEEK.indexOf(weekday);
  if (targetIdx === -1) return todayStr();

  const result = new Date(monday);
  result.setDate(result.getDate() + targetIdx);
  return result.toISOString().slice(0, 10);
}

/** Format "2026-03-19" as "19 Mar". */
export function formatShortDate(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  const day = d.getDate();
  const month = d.toLocaleString("en-GB", { month: "short" });
  return `${day} ${month}`;
}
//util func done by ai 