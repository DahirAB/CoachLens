import { useEffect, useState } from "react";
import { backendRequest } from "../../api/backendClient";

function isExpired(expiresAt) {
  if (!expiresAt) return false;
  return new Date(expiresAt).getTime() <= Date.now();
}

function formatDate(value) {
  if (!value) return "Never";
  return new Date(value).toLocaleDateString();
}

export default function SharedByMePanel({ refreshToken = 0 }) {
  const [shares, setShares] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [revokingId, setRevokingId] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    backendRequest("/api/plans/shared-by-me")
      .then((rows) => {
        if (!cancelled) setShares(rows);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load shares.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshToken]);

  async function handleRevoke(shareId) {
    setRevokingId(shareId);
    setError("");
    try {
      await backendRequest(`/api/plans/shares/${shareId}`, { method: "DELETE" });
      setShares((prev) =>
        prev.map((share) =>
          share.id === shareId
            ? { ...share, revoked_at: new Date().toISOString() }
            : share,
        ),
      );
    } catch (err) {
      setError(err.message || "Failed to revoke share.");
    } finally {
      setRevokingId("");
    }
  }

  return (
    <section className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6">
      <h2 className="text-base font-semibold text-white mb-1">Shares you created</h2>
      <p className="text-sm text-slate-400 mb-4">
        Manage access for users you have shared plans with.
      </p>

      {error && (
        <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Loading shares...</p>
      ) : shares.length === 0 ? (
        <p className="text-sm text-slate-500">No outgoing shares yet.</p>
      ) : (
        <div className="space-y-3">
          {shares.map((share) => {
            const revoked = Boolean(share.revoked_at);
            const expired = !revoked && isExpired(share.expires_at);
            const active = !revoked && !expired;
            return (
              <div
                key={share.id}
                className="rounded-xl border border-white/10 bg-white/3 px-4 py-3 flex items-center justify-between gap-4"
              >
                <div>
                  <p className="text-sm text-white">
                    @{share.recipient_username} <span className="text-slate-500">- plan</span> {share.plan_id.slice(0, 8)}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Tracking: {share.can_view_tracking ? "Allowed" : "Hidden"} | Expires: {formatDate(share.expires_at)}
                  </p>
                  <p className="text-xs mt-1 text-slate-500">
                    {revoked ? "Revoked" : expired ? "Expired" : "Active"}
                  </p>
                </div>
                {active && (
                  <button
                    onClick={() => handleRevoke(share.id)}
                    disabled={revokingId === share.id}
                    className="text-xs px-3 py-1.5 rounded-lg border border-red-500/30 text-red-300 hover:bg-red-500/10 disabled:opacity-50"
                  >
                    {revokingId === share.id ? "Revoking..." : "Revoke"}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
