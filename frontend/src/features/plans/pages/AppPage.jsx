import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import { backendRequest } from "../../../api/backendClient";
import DayCard from "../components/DayCard";

const DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

export default function AppPage() {
  const navigate = useNavigate();
  const { signOut } = useAuth();

  const [plan, setPlan] = useState(null);
  const [noPlan, setNoPlan] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchLatest() {
      try {
        const data = await backendRequest("/api/plans/latest");
        setPlan(data);
        setNoPlan(false);
      } catch (err) {
        if (err.status === 404) {
          setNoPlan(true);
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }
    fetchLatest();
  }, []);

  async function handleGenerate() {
    setError("");
    setGenerating(true);
    try {
      const data = await backendRequest("/api/plans/generate", { method: "POST" });
      setPlan(data);
      setNoPlan(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleSignOut() {
    await signOut();
    navigate("/");
  }

  const weekPlan = plan?.response_json?.week_plan;
  const split = plan?.response_json?.inferred_split;
  const sortedDays = weekPlan
    ? DAY_ORDER.filter((d) => weekPlan[d])
    : [];

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <header className="flex items-center justify-between px-8 py-5">
        <span className="text-sm font-bold text-white tracking-tight">CoachLens</span>
        <button
          onClick={handleSignOut}
          className="text-xs text-slate-400 hover:text-white border border-white/10 hover:border-white/30 rounded-lg px-3 py-1.5 transition-all duration-200"
        >
          Sign out
        </button>
      </header>

      <main className="max-w-5xl mx-auto px-6 pb-16">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">Your Plan</h1>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
          >
            {generating ? "Generating…" : noPlan ? "Generate my plan" : "Regenerate plan"}
          </button>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {loading && (
          <p className="text-slate-400 text-sm">Loading…</p>
        )}

        {!loading && noPlan && !error && (
          <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-12 text-center">
            <p className="text-slate-400 mb-1">No plan yet.</p>
            <p className="text-slate-500 text-sm">
              Hit "Generate my plan" to create your first training week.
            </p>
          </div>
        )}

        {plan?.status === "error" && (
          <div className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
            Plan generation failed: {plan.error_message}
          </div>
        )}

        {plan?.status === "success" && weekPlan && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {sortedDays.map((day) => (
              <DayCard
                key={day}
                day={day}
                split={split?.[day]}
                exercises={weekPlan[day]}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
