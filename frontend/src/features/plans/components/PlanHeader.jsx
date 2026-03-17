import { useEffect, useRef, useState } from "react";

export default function PlanHeader({ username, createdAt, onSignOut, onKebabAction }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleKebabItem(action) {
    onKebabAction?.(action);
    setDropdownOpen(false);
  }

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
      <div className="flex items-center gap-2">
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setDropdownOpen((o) => !o)}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            aria-label="Menu"
          >
            ⋮
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-52 rounded-xl border border-white/10 bg-black/60 backdrop-blur-xl shadow-lg overflow-hidden z-10">
              <button
                onClick={() => handleKebabItem("Sharing")}
                className="w-full text-left px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"
              >
                Share (soon)
              </button>
              <button
                onClick={() => handleKebabItem("Tracking")}
                className="w-full text-left px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"
              >
                Tracking (soon)
              </button>
              <div className="border-t border-white/10" />
              <button
                onClick={() => handleKebabItem("Delete plan")}
                className="w-full text-left px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"
              >
                Delete plan (soon)
              </button>
            </div>
          )}
        </div>
        <button
          onClick={onSignOut}
          className="text-xs text-slate-400 hover:text-white border border-white/10 hover:border-white/30 rounded-lg px-3 py-1.5 transition-all duration-200"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
