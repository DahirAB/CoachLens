export default function SelectField({ id, label, options, value, onChange }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-2">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-white/4 border border-white/8 rounded-xl px-4 py-3 text-sm text-white appearance-none focus:outline-none focus:border-cyan-400/50 focus:shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-all duration-200"
      >
        <option value="" disabled className="bg-canvas text-slate-400">
          Select...
        </option>
        {options.map((opt) => (
          <option key={opt} value={opt} className="bg-canvas text-white">
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}
