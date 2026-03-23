import { useEffect, useState } from "react";
import { backendRequest } from "../../api/backendClient";

function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleDateString();
}

export default function SharedWithMePanel({ onOpenShare }) {
  const [shares, setShares] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    backendRequest("/api/plans/shared-with-me")
      .then((rows) => {
        if (!cancelled) setShares(rows);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load shared plans.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-5">
      <h2 className="text-base font-semibold text-white mb-1">Shared with me</h2>
      <p className="text-sm text-slate-400 mb-4">Plans shared by other users.</p>

      {error && (
        <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-300">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Loading...</p>
      ) : shares.length === 0 ? (
        <p className="text-sm text-slate-500">No shared plans yet.</p>
      ) : (
        <div className="space-y-2">
          {shares.map((share) => (
            <button
              key={share.share_id}
              onClick={() => onOpenShare?.(share.share_id)}
              className="w-full text-left rounded-xl border border-white/10 bg-white/3 px-3 py-3 hover:border-white/20 transition-colors"
            >
              <p className="text-sm text-white font-medium mb-1">@{share.owner_username}</p>
              <p className="text-xs text-slate-400">Plan: {formatDate(share.plan_created_at)}</p>
              <p className="text-xs text-slate-400">Shared: {formatDate(share.shared_at)}</p>
              <p className="text-xs text-slate-500 mt-1">
                Tracking: {share.can_view_tracking ? "Visible" : "Hidden"}
              </p>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
