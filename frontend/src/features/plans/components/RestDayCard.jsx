import { DAY_LABEL } from "./DayCard";

export default function RestDayCard({ day }) {
  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-3 self-center">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="text-xs font-bold text-white uppercase tracking-wide">
          {DAY_LABEL[day] ?? day}
        </h3>
        <span className="text-xs text-slate-500">Rest</span>
      </div>
      <p className="text-[10px] text-slate-500 mt-0.5">Recovery day</p>
    </div>
  );
}
