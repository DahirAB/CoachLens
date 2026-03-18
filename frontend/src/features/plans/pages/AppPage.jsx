import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import { backendRequest } from "../../../api/backendClient";
import DayCard from "../components/DayCard";
import PlanHeader from "../components/PlanHeader";
import PlanMetaCard from "../components/PlanMetaCard";
import RestDayCard from "../components/RestDayCard";
import { useLatestPlan } from "../context/PlanContext";
import { hasConstraintsDrift } from "../utils/constraintsDrift";
import { buildRenderDays } from "../utils/weekRendering";

export default function AppPage() {
  const navigate = useNavigate();
  const { profile, signOut } = useAuth();
  const { plan, loading, noPlan, error, setError, refreshLatestPlan } = useLatestPlan();

  const [generating, setGenerating] = useState(false);

  async function handleGenerate() {
    setError("");
    setGenerating(true);
    try {
      await backendRequest("/api/plans/generate", { method: "POST" });
      await refreshLatestPlan();
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
  const inferredSplit = plan?.response_json?.inferred_split;
  const renderDays = buildRenderDays(weekPlan);
  const showConstraintsDrift = plan?.status === "success" && hasConstraintsDrift(plan, profile);
  const allWorkoutDays = weekPlan
    ? Object.keys(weekPlan).filter(d => Array.isArray(weekPlan[d]) && weekPlan[d].length > 0)
    : [];

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <PlanHeader
        username={profile?.username}
        createdAt={plan?.created_at}
        onSignOut={handleSignOut}
        onKebabAction={(action) => setError(`${action} is coming next.`)}
      />

      <main className="max-w-5xl mx-auto px-6 pb-16">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">Your Plan</h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/app/constraints")}
              className="text-sm text-slate-300 hover:text-white border border-white/10 hover:border-white/30 rounded-xl px-4 py-2.5 transition-all duration-200"
            >
              Edit constraints
            </button>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
            >
              {generating ? "Generating…" : noPlan ? "Generate my plan" : "Regenerate plan"}
            </button>
          </div>
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

        {showConstraintsDrift && (
          <div className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
            Your plan was generated with different constraints. Regenerate to apply your changes.
          </div>
        )}

        {plan?.status === "success" && weekPlan && (
          <>
            <PlanMetaCard requestJson={plan?.request_json} responseJson={plan?.response_json} />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {renderDays.map((item) =>
                item.type === "workout" ? (
                  <DayCard
                    key={item.day}
                    day={item.day}
                    split={inferredSplit?.[item.day]}
                    exercises={item.exercises}
                    createdAt={plan?.created_at}
                    allWorkoutDays={allWorkoutDays}
                  />
                ) : (
                  <RestDayCard key={item.day} day={item.day} />
                )
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
