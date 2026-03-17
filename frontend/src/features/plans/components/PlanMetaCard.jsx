import { DAY_LABEL } from "./DayCard";

function formatValue(val) {
  if (val == null) return "";
  return String(val);
}

function formatSplit(split) {
  if (!split) return "";
  return split.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function PlanMetaCard({ requestJson, responseJson }) {
  const req = requestJson ?? {};
  const res = responseJson ?? {};
  const trainingGoal = req.training_goal ? formatSplit(req.training_goal) : "";
  const availableDays = req.available_days;
  const daysLabel = Array.isArray(availableDays)
    ? availableDays.map((d) => DAY_LABEL[d] ?? d).join(", ")
    : formatValue(availableDays);
  const sessionLength =
    req.session_duration_minutes ?? req.session_duration_min ?? "";
  const equipment = Array.isArray(req.equipment)
    ? req.equipment.join(", ")
    : formatValue(req.equipment);

  const inferredSplit = res.inferred_split;
  const splitSummary =
    inferredSplit && typeof inferredSplit === "object"
      ? Object.entries(inferredSplit)
          .sort(([a], [b]) => {
            const order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
            return order.indexOf(a) - order.indexOf(b);
          })
          .map(([day, split]) => `${DAY_LABEL[day] ?? day}: ${formatSplit(split)}`)
          .join(", ")
      : "";

  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6 mb-8">
      <h2 className="text-base font-semibold text-white mb-4">Plan details</h2>
      <div className="grid sm:grid-cols-2 gap-6 text-sm">
        {trainingGoal && (
          <div>
            <p className="text-slate-400 mb-1">Training goal</p>
            <p className="text-slate-200">{trainingGoal}</p>
          </div>
        )}
        {daysLabel && (
          <div>
            <p className="text-slate-400 mb-1">Days</p>
            <p className="text-slate-200">{daysLabel}</p>
          </div>
        )}
        {sessionLength !== "" && (
          <div>
            <p className="text-slate-400 mb-1">Session length</p>
            <p className="text-slate-200">{sessionLength} min</p>
          </div>
        )}
        {equipment && (
          <div>
            <p className="text-slate-400 mb-1">Equipment</p>
            <p className="text-slate-200 capitalize">{equipment}</p>
          </div>
        )}
        {splitSummary && (
          <div className="sm:col-span-2">
            <p className="text-slate-400 mb-1">Inferred split</p>
            <p className="text-slate-200">{splitSummary}</p>
          </div>
        )}
      </div>
    </div>
  );
}
