export const DAY_LABEL = {
  monday: "Mon",
  tuesday: "Tue",
  wednesday: "Wed",
  thursday: "Thu",
  friday: "Fri",
  saturday: "Sat",
  sunday: "Sun",
};

export const SPLIT_COLORS = {
  push: "text-rose-400",
  pull: "text-sky-400",
  legs: "text-emerald-400",
  upper: "text-amber-400",
  lower: "text-violet-400",
  full_body: "text-cyan-400",
};

function exerciseDuration(ex) {
  return ex.sets* ex.work_minutes + ex.rest_minutes*(ex.sets-1);
}
fc
function dayDuration(exercises) {
  return exercises.reduce((sum, ex) => sum + exerciseDuration(ex), 0);
}

export default function DayCard({ day, split, exercises }) {
  const durationMinutes = dayDuration(exercises ?? []);
  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-5">
      <div className="flex items-baseline justify-between mb-4">
        <div className="flex items-baseline gap-2">
          <h3 className="text-sm font-bold text-white uppercase tracking-wide">
            {DAY_LABEL[day] ?? day}
          </h3>
          {durationMinutes > 0 && (
            <span className="text-xs text-slate-500">~{durationMinutes} min</span>
          )}
        </div>
        <span className={`text-xs font-medium ${SPLIT_COLORS[split] ?? "text-slate-400"}`}>
          {split?.replace("_", " ")}
        </span>
      </div>
      <div className="space-y-3">
        {exercises.map((ex, i) => {
          const equip = ex.equipment ?? "";
          const equipLabel = equip.charAt(0).toUpperCase() + equip.slice(1);
          const weightHint = ex.weight_display
            ? ex.weight_display.trim()
            : ex.weight_range_kg
              ? `${ex.weight_range_kg.min}-${ex.weight_range_kg.max} kg`
              : equip === "bodyweight"
                ? null
                : "Pick a weight you can complete reps/sets with";
          return (
            <div key={i} className="flex flex-col gap-0.5 text-sm">
              <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                {equipLabel}
              </span>
              <div className="flex items-center justify-between gap-2">
                <span className="text-slate-300 truncate flex-1 min-w-0">{ex.name}</span>
                {ex.rest_minutes != null && (
                  <span className="text-xs text-slate-500 shrink-0">
                    Rest {ex.rest_minutes} min
                  </span>
                )}
                <span className="text-slate-500 shrink-0">
                  {ex.sets} sets × {ex.rep_range} reps
                </span>
              </div>
              {weightHint && (
                <span className="text-xs text-slate-500">
                  {weightHint}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
