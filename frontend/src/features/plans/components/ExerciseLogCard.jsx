export default function ExerciseLogCard({
  day,
  exercises,
  entries,
  onToggleDone,
  onSetsChange,
}) {
  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6 mb-6">
      <h2 className="text-sm font-bold text-white uppercase tracking-wide mb-4">Exercises</h2>
      <div className="space-y-4">
        {exercises.map((ex, i) => {
          const key = `${day}:${i}`;
          const entry = entries[key] || { done: false, sets_done: 0 };
          const plannedSets = ex.sets ?? 0;
          const completed = entry.done || entry.sets_done >= plannedSets;
          return (
            <div
              key={key}
              className={`flex items-center gap-4 p-3 rounded-xl border transition-colors ${
                completed ? "bg-emerald-500/10 border-emerald-500/20" : "bg-white/5 border-white/10"
              }`}
            >
              <input
                type="checkbox"
                checked={entry.done}
                onChange={() => onToggleDone(key, plannedSets)}
                className="w-4 h-4 rounded border-white/30 bg-white/5 text-cyan-500 focus:ring-cyan-500/50"
              />
              <span
                className={`flex-1 text-sm ${
                  completed ? "text-emerald-300 line-through" : "text-slate-300"
                }`}
              >
                {ex.name}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => onSetsChange(key, -1, plannedSets)}
                  className="w-8 h-8 rounded-lg border border-white/20 text-slate-400 hover:text-white hover:bg-white/5 text-sm font-medium"
                >
                  -
                </button>
                <span className="w-8 text-center text-sm text-white">
                  {entry.sets_done ?? 0}/{plannedSets}
                </span>
                <button
                  type="button"
                  onClick={() => onSetsChange(key, 1, plannedSets)}
                  className="w-8 h-8 rounded-lg border border-white/20 text-slate-400 hover:text-white hover:bg-white/5 text-sm font-medium"
                >
                  +
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
