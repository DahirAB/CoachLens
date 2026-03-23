import { useState } from "react";
import { backendRequest } from "../../api/backendClient";

function toExpiresAt(dateText) {
  if (!dateText) return null;
  return `${dateText}T23:59:59Z`;
}

export default function SharePlanModal({ open, planId, onClose, onShared }) {
  const [username, setUsername] = useState("");
  const [canViewTracking, setCanViewTracking] = useState(false);
  const [expiresDate, setExpiresDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!open) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const trimmed = username.trim().toLowerCase();
    if (!trimmed) {
      setError("Username is required.");
      return;
    }
    if (!/^[a-z0-9_]{3,20}$/.test(trimmed) || !/[0-9]/.test(trimmed)) {
      setError("Use 3-20 letters, numbers, or underscores, and include at least one digit.");
      return;
    }

    setSubmitting(true);
    try {
      const result = await backendRequest(`/api/plans/${planId}/share`, {
        method: "POST",
        body: {
          username: trimmed,
          can_view_tracking: canViewTracking,
          expires_at: toExpiresAt(expiresDate),
        },
      });
      onShared?.(result);
      setUsername("");
      setCanViewTracking(false);
      setExpiresDate("");
      onClose?.();
    } catch (err) {
      setError(err.message || "Failed to share plan.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-canvas-deep p-6">
        <h2 className="text-lg font-semibold text-white mb-1">Share plan</h2>
        <p className="text-sm text-slate-400 mb-5">
          Share this plan with another user.
        </p>

        {error && (
          <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-slate-400 mb-2">Recipient username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. john1"
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/40"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-2">Expires on (optional)</label>
            <input
              type="date"
              value={expiresDate}
              onChange={(e) => setExpiresDate(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400/40"
            />
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={canViewTracking}
              onChange={(e) => setCanViewTracking(e.target.checked)}
              className="rounded border-white/20 bg-white/5"
            />
            <span className="text-sm text-slate-300">Allow recipient to view tracking logs</span>
          </label>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 rounded-lg text-sm border border-white/20 text-slate-200 hover:border-white/40 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-linear-to-r from-cyan-500 to-blue-500 text-white disabled:opacity-50"
            >
              {submitting ? "Sharing..." : "Share plan"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
