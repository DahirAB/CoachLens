import { DAY_LABEL } from "./DayCard";
import { formatShortDate } from "../utils/trackingDates";

export default function TrackingDateCard({ selectedDate, day, isRestDay }) {
  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6 mb-6">
      <p className="text-sm text-slate-300">
        {DAY_LABEL[day] ?? day} {selectedDate && formatShortDate(selectedDate)} –{" "}
        {isRestDay ? "Rest day" : "Workout day"}
      </p>
    </div>
  );
}
