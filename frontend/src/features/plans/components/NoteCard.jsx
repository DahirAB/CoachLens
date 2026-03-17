export default function NoteCard({ title, subtitle, noteText, onNoteChange, rows, placeholder }) {
  return (
    <div className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6 mb-6">
      {title && (
        <label className="block text-sm font-medium text-slate-400 mb-2">{title}</label>
      )}
      {subtitle != null && subtitle !== "" && (
        <p className="text-slate-400 text-sm mb-4">{subtitle}</p>
      )}
      <textarea
        placeholder={placeholder}
        value={noteText}
        onChange={onNoteChange}
        rows={rows}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 resize-none"
      />
    </div>
  );
}
