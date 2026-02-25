import { useState } from "react";
import { CheckIcon, InformationCircleIcon } from "@heroicons/react/24/outline";
import { EQUIPMENT } from "../constants";
import NumberField from "./NumberField";
import OneRmGuessModal from "./OneRmGuessModal";

export default function StepTwo({
  selectedEquipment,
  toggleEquipment,
  oneRepMaxes,
  setOneRepMax,
  includeCardio,
  setIncludeCardio,
}) {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <h2 className="text-xl font-semibold text-white mb-6">Equipment and lifts</h2>
      <div className="space-y-6">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-3">
            Available equipment
          </label>
          <div className="flex flex-wrap gap-2">
            {EQUIPMENT.map((item) => {
              const active = selectedEquipment.includes(item);
              return (
                <button
                  key={item}
                  type="button"
                  onClick={() => toggleEquipment(item)}
                  className={`px-4 py-2 text-xs font-medium rounded-full border transition-all duration-200 ${
                    active
                      ? "bg-cyan-500/20 border-cyan-400/40 text-cyan-300"
                      : "bg-white/4 border-white/10 text-slate-400 hover:bg-white/8 hover:text-white"
                  }`}
                >
                  {item}
                </button>
              );
            })}
          </div>
          <p className="text-xs text-slate-500 mt-3">
            If none selected, defaults to Bodyweight.
          </p>
        </div>

        <div>
          <div className="flex justify-between items-center mb-3">
            <label className="text-xs font-medium text-slate-400">
              One-rep maxes (kg)
              <span className="ml-1 text-amber-400/80">Required</span>
            </label>
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-300 hover:bg-white/8 border border-transparent hover:border-white/10 transition-colors"
            >
              <InformationCircleIcon className="w-4 h-4 shrink-0" />
              <span>1RM helper</span>
            </button>
          </div>
          <OneRmGuessModal
            open={modalOpen}
            onClose={() => setModalOpen(false)}
            setOneRepMax={setOneRepMax}
          />
          <div className="grid grid-cols-2 gap-4">
            <NumberField id="squat-1rm" label="Squat" placeholder="e.g. 120" value={oneRepMaxes.squat} onChange={(v) => setOneRepMax("squat", v)} />
            <NumberField id="bench-1rm" label="Bench" placeholder="e.g. 90" value={oneRepMaxes.bench} onChange={(v) => setOneRepMax("bench", v)} />
            <NumberField id="deadlift-1rm" label="Deadlift" placeholder="e.g. 150" value={oneRepMaxes.deadlift} onChange={(v) => setOneRepMax("deadlift", v)} />
            <NumberField id="ohp-1rm" label="OHP" placeholder="e.g. 55" value={oneRepMaxes.ohp} onChange={(v) => setOneRepMax("ohp", v)} />
          </div>
          <p className="text-xs text-slate-500 mt-3">
           If you don&apos;t know, make an educated guess.
          </p>
        </div>

        <label className="flex items-center gap-3 cursor-pointer group">
          <input
            type="checkbox"
            checked={includeCardio}
            onChange={(e) => setIncludeCardio(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-5 h-5 rounded-md border border-white/20 bg-white/4 flex items-center justify-center transition-all peer-checked:bg-cyan-500/20 peer-checked:border-cyan-400/40">
            {includeCardio && (
              <CheckIcon className="w-3.5 h-3.5 text-cyan-300" />
            )}
          </div>
          <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
            Include cardio in my plan
          </span>
        </label>
      </div>
    </>
  );
}
