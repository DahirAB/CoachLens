import { useEffect, useState, useCallback } from "react";
import { Link, Navigate, useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import { backendRequest } from "../../../api/backendClient";
import PlanHeader from "../components/PlanHeader";
import TrackingDateCard from "../components/TrackingDateCard";
import ExerciseLogCard from "../components/ExerciseLogCard";
import NoteCard from "../components/NoteCard";
import { useLatestPlan } from "../context/PlanContext";
import {
  dateToWeekday,
  todayStr,
  firstDateForWeekdayOnOrAfter,
} from "../utils/trackingDates";

export default function TrackingPage() {
  const navigate = useNavigate();
  const { profile, signOut } = useAuth();
  const [searchParams] = useSearchParams();
  const dateParam = searchParams.get("date");
  const dayParam = searchParams.get("day");
  const { plan, loading, noPlan, error, setError } = useLatestPlan();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [trackingLoading, setTrackingLoading] = useState(true);

  const [selectedDate, setSelectedDate] = useState(todayStr());
  const [entries, setEntries] = useState({});
  const [noteText, setNoteText] = useState("");

  const day = dateToWeekday(selectedDate);
  const weekPlan = plan?.response_json?.week_plan;
  const exercises = weekPlan?.[day];
  const isRestDay = !Array.isArray(exercises) || exercises.length === 0;

  useEffect(() => {
    const today = todayStr();
    if (dateParam) {
      setSelectedDate(dateParam > today ? today : dateParam);
      return;
    }
    if (!plan?.created_at || !dayParam) return;
    const refDateStr = plan.created_at.slice(0, 10);
    const resolved = firstDateForWeekdayOnOrAfter(dayParam, refDateStr);
    setSelectedDate(resolved > today ? today : resolved);
  }, [plan?.created_at, dayParam, dateParam]);

  const loadExistingTracking = useCallback(
    async (planId, dateStr) => {
      if (!planId) return;
      try {
        const row = await backendRequest(
          `/api/plans/${planId}/tracking/daily?logged_date=${encodeURIComponent(dateStr)}`
        );
        setEntries(row?.entries_json || {});
        setNoteText(row?.note_text || "");
      } catch (err) {
        if (err.status === 404) {
          setEntries({});
          setNoteText("");
        } else {
          setError(err.message);
        }
      }
    },
    []
  );

  useEffect(() => {
    if (!plan?.id || !selectedDate) {
      setTrackingLoading(false);
      return;
    }
    setTrackingLoading(true);
    loadExistingTracking(plan.id, selectedDate).finally(() =>
      setTrackingLoading(false)
    );
  }, [plan?.id, selectedDate, loadExistingTracking]);

  const updateEntry = (slotKey, updates) => {
    setEntries((prev) => {
      const next = { ...prev, [slotKey]: { ...prev[slotKey], ...updates } };
      return next;
    });
    setSaved(false);
  };

  const handleDoneToggle = (slotKey, plannedSets) => {
    setEntries((prev) => {
      const cur = prev[slotKey];
      const done = !cur?.done;
      return {
        ...prev,
        [slotKey]: {
          ...cur,
          done,
          sets_done: done ? plannedSets : 0,
        },
      };
    });
    setSaved(false);
  };

  const handleSetsChange = (slotKey, change, plannedSets) => {
    setEntries((prev) => {
      const cur = prev[slotKey] || { sets_done: 0 };
      const nextVal = Math.max(0, Math.min(plannedSets, (cur.sets_done || 0) + change));
      return {
        ...prev,
        [slotKey]: { ...cur, sets_done: nextVal, done: nextVal >= plannedSets },
      };
    });
    setSaved(false);
  };

  const handleNoteChange = (e) => {
    setNoteText(e.target.value);
    setSaved(false);
  };

  async function handleSubmit() {
    if (!plan?.id) return;
    setError("");
    setSaving(true);
    try {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const bodyEntries = {};
      if (!isRestDay && exercises) {
        exercises.forEach((ex, i) => {
          const key = `${day}:${i}`;
          const cur = entries[key];
          bodyEntries[key] = {
            exercise_name: ex.name,
            done: cur?.done ?? false,
            sets_done: cur?.sets_done ?? 0,
          };
        });
      }
      await backendRequest(`/api/plans/${plan.id}/tracking/daily`, {
        method: "PUT",
        body: {
          day,
          logged_date: selectedDate,
          timezone,
          note_text: noteText || null,
          entries: bodyEntries,
        },
      });
      navigate("/app");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleSignOut() {
    await signOut();
    window.location.href = "/";
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
        <main className="max-w-5xl mx-auto px-6 py-12">
          <p className="text-slate-400 text-sm">Loading…</p>
        </main>
      </div>
    );
  }

  if (noPlan) {
    return <Navigate to="/app" replace />;
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <PlanHeader
        username={profile?.username}
        createdAt={plan?.created_at}
        onSignOut={handleSignOut}
        onKebabAction={() => {}}
      />

      <main className="max-w-5xl mx-auto px-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Log workout</h1>
          <Link
            to="/app"
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Back to plan
          </Link>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <TrackingDateCard
          selectedDate={selectedDate}
          day={day}
          isRestDay={isRestDay}
        />

        {trackingLoading ? (
          <p className="text-slate-400 text-sm py-8">Loading workout…</p>
        ) : (
          <>
            {isRestDay ? (
              <NoteCard
                title={null}
                subtitle="Rest day - add a note if you like."
                noteText={noteText}
                onNoteChange={handleNoteChange}
                rows={3}
                placeholder="Optional note…"
              />
            ) : (
              <ExerciseLogCard
                day={day}
                exercises={exercises}
                entries={entries}
                onToggleDone={handleDoneToggle}
                onSetsChange={handleSetsChange}
              />
            )}

            {!isRestDay && (
              <NoteCard
                title="Note (optional)"
                subtitle={null}
                noteText={noteText}
                onNoteChange={handleNoteChange}
                rows={2}
                placeholder="How did it go?"
              />
            )}

            <div className="flex items-center gap-4">
              <button
                onClick={handleSubmit}
                disabled={saving}
                className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
              >
                {saving ? "Saving…" : "Save workout log"}
              </button>
              {saved && (
                <span className="text-sm text-emerald-400">Saved</span>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
