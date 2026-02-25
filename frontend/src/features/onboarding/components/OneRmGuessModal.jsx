import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { ONE_RM_GUESSES } from "../constants";

const EXPERIENCE_LEVELS = ["beginner", "intermediate", "advanced"];

export default function OneRmGuessModal({ open, onClose, setOneRepMax }) {
  const [gender, setGender] = useState("male");
  const [experience, setExperience] = useState("beginner");

  useEffect(() => {
    if (!open) return;
    function handleEscape(e) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleEscape);
    
    return () => {
      document.removeEventListener("keydown", handleEscape);
     
    };
  }, [open, onClose]);

  if (!open) return null;

  const rows = ONE_RM_GUESSES[gender]?.[experience] ?? [];

  const modalContent = (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-md"
          onClick={onClose}/>

     
      <div className="relative w-full max-w-lg max-h-[90vh] overflow-hidden rounded-2xl border border-white/10 bg-slate-900/95 shadow-2xl"
          onClick={(e) => e.stopPropagation()}>
        <div className="p-6 space-y-6 overflow-y-auto max-h-[90vh]">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">
              Educated guesses
            </h2>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors">
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          <div>
            <span className="block text-sm font-medium text-slate-400 mb-2">Gender</span>
            <div className="flex gap-3">
              {["male", "female"].map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGender(g)}
                  className={`px-5 py-2.5 text-sm font-medium rounded-full border transition-all duration-200 ${
                    gender === g
                      ? "bg-cyan-500/20 border-cyan-400/40 text-cyan-300"
                      : "bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {g === "male" ? "Male" : "Female"}
                </button>
              ))}
            </div>
          </div>

          <div>
            <span className="block text-sm font-medium text-slate-400 mb-2">Experience</span>
            <div className="flex flex-wrap gap-2">
              {EXPERIENCE_LEVELS.map((exp) => (
                <button
                  key={exp}
                  type="button"
                  onClick={() => setExperience(exp)}
                  className={`px-4 py-2 text-sm font-medium rounded-full border transition-all duration-200 ${
                    experience === exp
                      ? "bg-cyan-500/20 border-cyan-400/40 text-cyan-300"
                      : "bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {exp.charAt(0).toUpperCase() + exp.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <span className="block text-sm font-medium text-slate-400">Select a profile</span>
            {rows.map((row, i) => (
              <div
                key={i}
                className="flex flex-wrap items-center gap-4 py-3 px-4 rounded-xl bg-white/5 border border-white/10"
              >
                <span className="text-slate-200 font-medium">
                  {row.weight}kg / {row.height}cm
                </span>
                <span className="text-slate-500 text-sm">
                  S:{row.squat} B:{row.bench} D:{row.deadlift} O:{row.ohp}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setOneRepMax("squat", row.squat);
                    setOneRepMax("bench", row.bench);
                    setOneRepMax("deadlift", row.deadlift);
                    setOneRepMax("ohp", row.ohp);
                    onClose();
                  }}
                  className="ml-auto px-4 py-2 text-sm font-medium rounded-lg bg-cyan-500/20 border border-cyan-400/40 text-cyan-300 hover:bg-cyan-500/30 transition-colors"
                >
                  Use
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
