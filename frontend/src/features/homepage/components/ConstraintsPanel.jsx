import { constraintsPanelModel } from "./constraintsPanelModel";

export default function ConstraintsPanel() {
  const model = constraintsPanelModel;

  

  return (
    <div className="relative">
      <div className="absolute inset-0 bg-linear-to-br from-cyan-500/6 to-blue-500/4 rounded-3xl blur-xl" />

      <div className="relative backdrop-blur-lg bg-white/4 border border-white/8 rounded-3xl p-6 shadow-[0_0_40px_rgba(0,150,255,0.08)]">
        <h3 className="text-base font-semibold text-white mb-5">{model.title}</h3>

        <div className="flex flex-wrap gap-2 mb-6">
          {model.Tags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-white/6 border border-white/10 rounded-full hover:bg-white/10 hover:text-white transition-colors"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs">
          <div className="bg-white/3 rounded-xl p-4 border border-white/6">
            <h4 className="text-slate-400 font-semibold mb-3 uppercase tracking-wide text-[10px]">
              Must Satisfy
            </h4>
            <ul className="space-y-2 text-slate-300">
              {model.mustSatisfy.map((item, index) => (
                <li key={index} className="flex items-start gap-1.5">
                  <span className="text-cyan-400 mt-0.5">•</span>
                  <span>{item.label}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white/3 rounded-xl p-4 border border-white/6">
            <h4 className="text-slate-400 font-semibold mb-3 uppercase tracking-wide text-[10px]">
              Optimises For
            </h4>
            <ul className="space-y-2 text-slate-300">
              {model.optimisesFor.map((item, index) => (
                <li key={index} className="flex items-start gap-1.5">
                  <span className="text-amber-400 mt-0.5">•</span>
                  <span>{item.label}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
