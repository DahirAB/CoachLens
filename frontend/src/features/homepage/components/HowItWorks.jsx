import {
  Cog6ToothIcon,
  BoltIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
} from "@heroicons/react/24/outline";

const howItWorksSteps = [
  { Icon: Cog6ToothIcon, label: "Input constraints" },
  { Icon: BoltIcon, label: "Optimiser runs" },
  { Icon: DocumentTextIcon, label: "Plan generated" },
  { Icon: CalendarDaysIcon, label: "View Weekly Plan" },
];

function Step({ Icon, label, isLast }) {
  return (
    <div className="flex items-center">
      <div className="group flex flex-col items-center text-center flex-1">
        <div className="mb-4 p-4 rounded-2xl bg-white/5 border border-white/10 group-hover:bg-linear-to-br group-hover:from-cyan-500/20 group-hover:to-blue-500/20 group-hover:border-cyan-400/30 group-hover:shadow-[0_0_30px_rgba(6,182,212,0.2)] transition-all duration-300">
          <Icon className="w-12 h-12 text-cyan-400 group-hover:text-cyan-300 group-hover:scale-105 transition-all duration-300" />
        </div>
        <h4 className="text-sm font-medium text-white/90 group-hover:text-white transition-colors duration-200">
          {label}
        </h4>
      </div>
      
      {!isLast && (
        <div className="hidden md:block w-16 h-px bg-linear-to-r from-cyan-500/40 via-blue-500/40 to-cyan-500/40 mx-4 mb-8" />
      )}
    </div>
  );
}

export default function HowItWorks() {
  return (
    <div className="relative animate-[fadeIn_0.8s_ease-out]">
      <div className="absolute inset-0 bg-linear-to-br from-cyan-500/5 to-blue-500/5 rounded-3xl blur-2xl" />

      <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12 md:p-14 shadow-[0_0_60px_rgba(0,150,255,0.1)]">
        <h2 className="text-2xl font-bold text-white text-center mb-14">
          How it works
        </h2>

        <div className="grid grid-cols-2 md:flex md:justify-between gap-8 md:gap-0">
          {howItWorksSteps.map((step, index) => (
            <Step
              key={index}
              Icon={step.Icon}
              label={step.label}
              isLast={index === howItWorksSteps.length - 1}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
