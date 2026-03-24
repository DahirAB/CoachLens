import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { backendRequest } from "../../api/backendClient";
import DayCard from "../plans/components/DayCard";
import PlanMetaCard from "../plans/components/PlanMetaCard";
import RestDayCard from "../plans/components/RestDayCard";
import { buildRenderDays } from "../plans/utils/weekRendering";
import { todayStr, capitalizeWeekday } from "../plans/utils/trackingDates";

function formatLongDate(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function renderTrackingEntries(entriesJson = {}) {
  const items = Object.entries(entriesJson);
  if (items.length === 0) return <p className="text-xs text-slate-500">No exercise logs on this date.</p>;
  return (
    <div className="space-y-2">
      {items.map(([slot, entry]) => {
        const [, rawIdx = "0"] = String(slot).split(":");
        const slotNumber = Number(rawIdx) + 1;
        const done = Boolean(entry.done);
        return (
          <div
            key={slot}
            className="rounded-xl border border-white/10 bg-white/4 px-3 py-2.5 flex items-center justify-between gap-3"
          >
            <div className="min-w-0">
              <p className="text-xs text-slate-500 uppercase tracking-wide">Exercise {slotNumber}</p>
              <p className="text-sm text-slate-200 truncate">{entry.exercise_name || "Exercise"}</p>
            </div>
            <div className="text-right shrink-0">
              <p className={`text-xs font-medium ${done ? "text-emerald-300" : "text-slate-400"}`}>
                {done ? "Completed" : "Not completed"}
              </p>
              <p className="text-xs text-slate-400">{entry.sets_done ?? 0} sets logged</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function SharedPlanViewPage() {
  const { shareId } = useParams();
  const [detail, setDetail] = useState(null);
  const [trackingRows, setTrackingRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [error, setError] = useState("");
  const [trackingError, setTrackingError] = useState("");
  const [selectedDate, setSelectedDate] = useState(todayStr());

  useEffect(() => {
    if (!shareId) return;
    let cancelled = false;
    setLoading(true);
    setError("");
    backendRequest(`/api/plans/shares/${shareId}`)
      .then((payload) => {
        if (!cancelled) setDetail(payload);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load shared plan.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [shareId]);

  useEffect(() => {
    if (!detail?.can_view_tracking || !shareId) {
      setTrackingRows([]);
      return;
    }
    let cancelled = false;
    setTrackingLoading(true);
    setTrackingError("");
    backendRequest(`/api/plans/shares/${shareId}/tracking/all`)
      .then((rows) => {
        if (cancelled) return;
        setTrackingRows(rows);
        const dates = rows.map((row) => row.logged_date);
        if (dates.length === 0) return;
        if (!dates.includes(selectedDate)) {
          setSelectedDate(dates[0]);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setTrackingRows([]);
          setTrackingError(err.message || "Failed to load tracking.");
        }
      })
      .finally(() => {
        if (!cancelled) setTrackingLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [detail?.can_view_tracking, shareId]);

  const weekPlan = detail?.response_json?.week_plan;
  const inferredSplit = detail?.response_json?.inferred_split;
  const renderDays = buildRenderDays(weekPlan);
  const trackingDates = trackingRows.map((row) => row.logged_date);
  const tracking = selectedDate
    ? trackingRows.find((row) => row.logged_date === selectedDate) ?? null
    : null;
  const selectedWeekday = capitalizeWeekday(selectedDate);
  const loggedWeekdaysText = trackingDates.map((dateStr) => capitalizeWeekday(dateStr)).join(", ");
  let nextTrackingDate = null;
  let previousTrackingDate = null;
  if (trackingDates.length && selectedDate) {
    const idx = trackingDates.indexOf(selectedDate);
    nextTrackingDate = trackingDates[idx + 1] ?? null;
    previousTrackingDate = idx > 0 ? trackingDates[idx - 1] : null;
  }
  const allWorkoutDays = weekPlan
    ? Object.keys(weekPlan).filter((day) => Array.isArray(weekPlan[day]) && weekPlan[day].length > 0)
    : [];

  function handlePreviousTrackingLog() {
    setSelectedDate(previousTrackingDate);
  }

  function handleNextTrackingLog() {
    setSelectedDate(nextTrackingDate);
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Shared plan</h1>
            {detail && <p className="text-sm text-slate-400 mt-1">Shared by @{detail.owner_username}</p>}
          </div>
          <Link to="/app" className="text-sm text-slate-400 hover:text-white transition-colors">
            Back
          </Link>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-sm text-slate-400">Loading...</p>
        ) : detail ? (
          <>
            <PlanMetaCard requestJson={detail.request_json} responseJson={detail.response_json} />

            {detail.can_view_tracking && (
              <section className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-5 mb-8">
                <div className="flex items-end justify-between gap-4 mb-4">
                  <div>
                    <h2 className="text-base font-semibold text-white">Shared tracking</h2>
                    <p className="text-xs text-slate-400 mt-1">
                      Workout logs from @{detail.owner_username} for {selectedWeekday}.
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Showing {formatLongDate(selectedDate)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {previousTrackingDate && (
                      <button
                        type="button"
                        onClick={handlePreviousTrackingLog}
                        disabled={trackingLoading}
                        className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:border-white/25 transition-colors disabled:opacity-50"
                      >
                        {trackingLoading ? "Loading..." : "Back log"}
                      </button>
                    )}
                    {nextTrackingDate && (
                      <button
                        type="button"
                        onClick={handleNextTrackingLog}
                        disabled={trackingLoading}
                        className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:border-white/25 transition-colors disabled:opacity-50"
                      >
                        {trackingLoading ? "Loading..." : "Next log"}
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-slate-500 mb-2">
                  {loggedWeekdaysText ? `Logged days: ${loggedWeekdaysText}.` : "No logged days available."}
                </p>
                {trackingLoading && <p className="text-xs text-slate-400 mb-2">Loading tracking...</p>}
                {trackingError && <p className="text-xs text-red-300 mb-2">{trackingError}</p>}
                {tracking ? (
                  <>
                    {renderTrackingEntries(tracking.entries_json)}
                    {tracking.note_text && (
                      <div className="mt-3 rounded-lg border border-white/10 bg-white/3 px-3 py-2">
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Note</p>
                        <p className="text-sm text-slate-300 whitespace-pre-wrap">{tracking.note_text}</p>
                      </div>
                    )}
                  </>
                ) : (
                  !trackingLoading && <p className="text-xs text-slate-500">No logged workouts yet.</p>
                )}
              </section>
            )}

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {renderDays.map((item) =>
                item.type === "workout" ? (
                  <DayCard
                    key={item.day}
                    day={item.day}
                    split={inferredSplit?.[item.day]}
                    exercises={item.exercises}
                    createdAt={detail.plan_created_at || detail.shared_at}
                    allWorkoutDays={allWorkoutDays}
                    readOnly={true}
                  />
                ) : (
                  <RestDayCard key={item.day} day={item.day} />
                ),
              )}
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}
