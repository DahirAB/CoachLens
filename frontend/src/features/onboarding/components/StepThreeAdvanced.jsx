import { useState } from "react";

const MAX_REQUIRED_LIFTS = 3;
const EXCLUSION_SOFT_WARN = 5;

export default function StepThreeAdvanced({
  catalog,
  loading,
  error,
  requiredPrimaryLifts,
  toggleRequiredLift,
  excludedExercises,
  toggleExcludedExercise,
  selectedEquipment,
  includeCardio,
}) {
  const [search, setSearch] = useState("");

  const normalizedEquip = new Set(selectedEquipment.map((e) => e.toLowerCase()));

  const filteredExercises = (catalog?.exercises || []).filter((ex) => {
    if (!includeCardio && ex.is_cardio) return false;
    if (!ex.equipment.some((eq) => normalizedEquip.has(eq))) return false;
    if (search && !ex.label.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
        Failed to load exercise catalog. Please go back and try again.
      </div>
    );
  }

  return (
    <>
      <h2 className="text-xl font-semibold text-white mb-6">Advanced options</h2>
      <div className="space-y-6">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-3">
            Required primary lifts
            <span className="ml-1 text-slate-500">
              ({requiredPrimaryLifts.length}/{MAX_REQUIRED_LIFTS})
            </span>
          </label>
          <div className="flex flex-wrap gap-2">
            {(catalog?.primary_lifts || []).map((lift) => {
              const active = requiredPrimaryLifts.includes(lift.id);
              const disabled = !active && requiredPrimaryLifts.length >= MAX_REQUIRED_LIFTS;
              return (
                <button
                  key={lift.id}
                  type="button"
                  disabled={disabled}
                  onClick={() => toggleRequiredLift(lift.id)}
                  className={`px-4 py-2 text-xs font-medium rounded-full border transition-all duration-200 ${
                    active
                      ? "bg-cyan-500/20 border-cyan-400/40 text-cyan-300"
                      : disabled
                        ? "bg-white/2 border-white/6 text-slate-600 cursor-not-allowed"
                        : "bg-white/4 border-white/10 text-slate-400 hover:bg-white/8 hover:text-white"
                  }`}
                >
                  {lift.label}
                </button>
              );
            })}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            The engine will guarantee these type of lifts appear in your plan.
          </p>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-3">
            Exclude exercises
            <span className="ml-1 text-slate-500">
              ({excludedExercises.length} selected)
            </span>
          </label>

          <div className="relative mb-3">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search exercises…"
              className="w-full bg-white/4 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/40 focus:ring-1 focus:ring-cyan-400/20 transition-all"
            />
          </div>

          <div className="max-h-48 overflow-y-auto space-y-1 rounded-xl border border-white/6 bg-white/2 p-2 scrollbar-thin scrollbar-thumb-white/10">
            {filteredExercises.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-3">
                {search ? "No exercises match your search." : "No exercises available for your equipment."}
              </p>
            ) : (
              filteredExercises.map((ex) => {
                const active = excludedExercises.includes(ex.id);
                return (
                  <button
                    key={ex.id}
                    type="button"
                    onClick={() => toggleExcludedExercise(ex.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all duration-150 flex items-center justify-between ${
                      active
                        ? "bg-red-500/10 border border-red-500/20 text-red-300"
                        : "hover:bg-white/6 text-slate-400 hover:text-white border border-transparent"
                    }`}
                  >
                    <span>{ex.label}</span>
                    {active && (
                      <span className="text-[10px] font-medium text-red-400 uppercase tracking-wide">
                        excluded
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>

          {excludedExercises.length >= EXCLUSION_SOFT_WARN && (
            <p className="text-xs text-amber-400/80 mt-2">
              Excluding many exercises may reduce plan feasibility.
            </p>
          )}
        </div>
      </div>
    </>
  );
}
