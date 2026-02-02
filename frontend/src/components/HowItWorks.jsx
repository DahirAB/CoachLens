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

function Step({ Icon, label }) {
  return (
    <div className="flex flex-col items-center text-center">
      <div className="mb-4">
        <Icon className="w-8 h-8 text-amber-500" />
      </div>
      <h4 className="text-sm font-medium text-surface-primary">{label}</h4>
    </div>
  );
}

export default function HowItWorks() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
      {howItWorksSteps.map((step, index) => (
        <Step key={index} Icon={step.Icon} label={step.label} />
      ))}
    </div>
  );
}
