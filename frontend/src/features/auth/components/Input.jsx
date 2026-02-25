import { InformationCircleIcon } from "@heroicons/react/24/outline";

const PASSWORD_HINT = "Atleast one lowercase, uppercase, digit and symbol";

export default function Input({ id, label, type = "text", value, onChange, placeholder, passwordWithHint, hasError, ...rest }) {
  const showHint = type === "password" && passwordWithHint;

  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full bg-white/4 border rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/50 focus:shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-all duration-200 ${
            hasError ? "border-red-500/40" : "border-white/8"
          } ${showHint ? "pr-10" : ""}`}
          {...rest}
        />
        {showHint && (
          <div className="absolute top-1/2 right-3 -translate-y-1/2 group ">
            <InformationCircleIcon className="w-5 h-5 text-slate-500 hover:text-slate-400 transition-colors" />
            <div className="absolute right-0 top-full mt-1 w-48 px-3 py-2 text-xs text-white bg-slate-800 border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-10 pointer-events-none">
              {PASSWORD_HINT}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
