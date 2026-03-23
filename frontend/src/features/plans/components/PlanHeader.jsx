export default function PlanHeader({ username, createdAt, onSignOut }) {

  return (
    <header className="flex items-center justify-between px-8 py-5">
      <div className="flex items-center gap-3">
        <span className="text-sm font-bold text-white tracking-tight">CoachLens</span>
        {username && (
          <span className="text-sm text-slate-400">@{username}</span>
        )}
        {createdAt && (
          <span className="text-sm text-slate-500">
            {new Date(createdAt).toLocaleDateString()}
          </span>
        )}
      </div>
      <button
        onClick={onSignOut}
        className="text-xs text-slate-400 hover:text-white border border-white/10 hover:border-white/30 rounded-lg px-3 py-1.5 transition-all duration-200"
      >
        Sign out
      </button>
    </header>
  );
}
