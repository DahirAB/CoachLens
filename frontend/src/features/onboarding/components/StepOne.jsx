import { WEEKDAYS, DURATIONS, GOALS } from "../constants";
import SelectField from "./SelectField";

export default function StepOne({ selectedDays, toggleDay, duration, setDuration, goal, setGoal }) {
  return (
    <>
      <h2 className="text-xl font-semibold text-white mb-6">Core constraints</h2>
      <div className="space-y-5">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-3">
            Training days
          </label>
          <div className="flex flex-wrap gap-2">
            {WEEKDAYS.map((day) => {
              const active = selectedDays.includes(day);
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => toggleDay(day)}
                  className={`px-4 py-2 text-xs font-medium rounded-full border transition-all duration-200 ${
                    active
                      ? "bg-cyan-500/20 border-cyan-400/40 text-cyan-300"
                      : "bg-white/4 border-white/10 text-slate-400 hover:bg-white/8 hover:text-white"
                  }`}
                >
                  {day.slice(0, 3)}
                </button>
              );
            })}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            id="session-duration"
            label="Session length"
            options={DURATIONS}
            value={duration}
            onChange={setDuration}
          />
          <SelectField
            id="training-goal"
            label="Training goal"
            options={GOALS}
            value={goal}
            onChange={setGoal}
          />
        </div>
      </div>
    </>
  );
}
