export default function NumberField({ id, label, placeholder, value, onChange }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-400 mb-2">
        {label}
      </label>
      <input
        id={id}
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-white/4 border border-white/8 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/50 focus:shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-all duration-200"
        placeholder={placeholder}
      />
    </div>
  );
}
