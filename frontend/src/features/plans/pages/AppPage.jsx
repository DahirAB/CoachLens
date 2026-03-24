import { useState, useEffect } from "react";
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
import SharePlanModal from "../../sharing/SharePlanModal";
import SharedByMePanel from "../../sharing/SharedByMePanel";
import SharedWithMePanel from "../../sharing/SharedWithMePanel";

export default function AppPage() {
  const navigate = useNavigate();
  const { profile, signOut, refreshProfile } = useAuth();
  const { plan, loading, noPlan, error, setError, refreshLatestPlan, viewingOldPlan, viewPlan } = useLatestPlan();

  const [generating, setGenerating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [sharePanelRefreshToken, setSharePanelRefreshToken] = useState(0);
  const [progressStatus, setProgressStatus] = useState(null);
  const [progressing, setProgressing] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");

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

  function handleDeletePlanClick() {
    if (!plan?.id) {
      setError("No plan selected to delete.");
      return;
    }
    setDeleteConfirmOpen(true);
  }

  async function confirmDeletePlan() {
    setError("");
    setDeleting(true);
    try {
      await backendRequest(`/api/plans/${plan.id}`, { method: "DELETE" });
      await refreshLatestPlan();
      setSharePanelRefreshToken((value) => value + 1);
      setDeleteConfirmOpen(false);
    } catch (err) {
      setError(err.message || "Failed to delete plan.");
    } finally {
      setDeleting(false);
    }
  }

  const showConstraintsDrift = !viewingOldPlan && plan?.status === "success" && hasConstraintsDrift(plan, profile);

  useEffect(() => {
    if (!plan?.id || plan.status !== "success" || showConstraintsDrift) {
      setProgressStatus(null);
      return;
    }
    backendRequest(`/api/plans/${plan.id}/progress/status`)
      .then(setProgressStatus)
      .catch(() => setProgressStatus(null));
  }, [plan?.id, plan?.status, showConstraintsDrift]);

  async function handleProgress() {
    if (!progressStatus?.can_progress) {
      setProgressMessage(
        `Log all training days first (${progressStatus?.days_logged ?? 0} of ${progressStatus?.days_total ?? 0} logged)`
      );
      return;
    }
    setProgressMessage("");
    setProgressing(true);
    try {
      await backendRequest(`/api/plans/${plan.id}/progress`, { method: "POST" });
      await refreshProfile();
      await refreshLatestPlan();
    } catch (err) {
      setError(err.message);
    } finally {
      setProgressing(false);
    }
  }

  const weekPlan = plan?.response_json?.week_plan;
  const inferredSplit = plan?.response_json?.inferred_split;
  const renderDays = buildRenderDays(weekPlan);
  const allWorkoutDays = weekPlan
    ? Object.keys(weekPlan).filter(d => Array.isArray(weekPlan[d]) && weekPlan[d].length > 0)
    : [];

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <PlanHeader
        username={profile?.username}
        createdAt={plan?.created_at}
        onSignOut={handleSignOut}
      />

      <main className="max-w-7xl mx-auto px-6 pb-16">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">
            Week {plan?.week_number ?? 1} Plan
          </h1>
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            {plan?.parent_plan_id && (
              <button
                onClick={() => viewPlan(plan.parent_plan_id)}
                className="text-xs sm:text-sm text-slate-300 hover:text-white border border-white/10 hover:border-white/30 rounded-xl px-3 py-2 sm:px-4 sm:py-2.5 transition-all duration-200"
              >
                Previous week
              </button>
            )}
            {viewingOldPlan && (
              <button
                onClick={refreshLatestPlan}
                className="text-xs sm:text-sm font-semibold bg-linear-to-r from-cyan-500 to-blue-500 text-white px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300"
              >
                Back to current week
              </button>
            )}
            {!viewingOldPlan && (
              <>
                <button
                  onClick={() => navigate("/app/constraints")}
                  className="text-xs sm:text-sm text-slate-300 hover:text-white border border-white/10 hover:border-white/30 rounded-xl px-3 py-2 sm:px-4 sm:py-2.5 transition-all duration-200"
                >
                  Edit constraints
                </button>
                {plan?.status === "success" && (
                  <button
                    onClick={() => setShareModalOpen(true)}
                    className="text-xs sm:text-sm text-slate-300 hover:text-white border border-white/10 hover:border-white/30 rounded-xl px-3 py-2 sm:px-4 sm:py-2.5 transition-all duration-200"
                  >
                    Share
                  </button>
                )}
                <button
                  onClick={handleDeletePlanClick}
                  disabled={!plan?.id || deleting}
                  className="text-xs sm:text-sm text-red-300 hover:text-red-200 border border-red-500/30 hover:border-red-500/50 rounded-xl px-3 py-2 sm:px-4 sm:py-2.5 transition-all duration-200"
                >
                  {deleting ? "Deleting..." : "Delete plan"}
                </button>
                {plan?.status === "success" && !showConstraintsDrift && progressStatus && (
                  <button
                    onClick={handleProgress}
                    disabled={progressing}
                    className="text-xs sm:text-sm font-semibold bg-linear-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl hover:shadow-[0_0_30px_rgba(0,200,150,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {progressing
                      ? "Progressing…"
                      : `Progress to week ${plan.week_number + 1}`}
                  </button>
                )}
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="text-xs sm:text-sm font-semibold bg-linear-to-r from-cyan-500 to-blue-500 text-white px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
                >
                  {generating ? "Generating…" : noPlan ? "Generate my plan" : "Regenerate plan"}
                </button>
              </>
            )}
          </div>
        </div>

        {progressMessage && (
          <div className="mb-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
            {progressMessage}
          </div>
        )}

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <section>
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
          </section>

          <aside className="space-y-6 xl:sticky xl:top-6 self-start">
            <SharedWithMePanel onOpenShare={(id) => navigate(`/app/shared/${id}`)} />
            <SharedByMePanel refreshToken={sharePanelRefreshToken} />
          </aside>
        </div>
      </main>
      <SharePlanModal
        open={shareModalOpen}
        planId={plan?.id}
        onClose={() => setShareModalOpen(false)}
        onShared={() => {
          setError("");
          setSharePanelRefreshToken((value) => value + 1);
        }}
      />
      {deleteConfirmOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-2xl border border-white/10 bg-canvas-deep p-6">
            <h2 className="text-lg font-semibold text-white mb-2">Delete plan?</h2>
            <p className="text-sm text-slate-300 mb-2">
              This will permanently delete this plan and its related shares and tracking logs.
            </p>
            <p className="text-sm text-slate-400 mb-5">
              If you want a new plan, why don&apos;t you regenerate your constraints and make a new plan instead?
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setDeleteConfirmOpen(false)}
                disabled={deleting}
                className="px-4 py-2 rounded-lg text-sm border border-white/20 text-slate-200 hover:border-white/40 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmDeletePlan}
                disabled={deleting}
                className="px-4 py-2 rounded-lg text-sm font-semibold border border-red-500/30 text-red-200 hover:bg-red-500/10 disabled:opacity-50"
              >
                {deleting ? "Deleting..." : "Delete plan"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
