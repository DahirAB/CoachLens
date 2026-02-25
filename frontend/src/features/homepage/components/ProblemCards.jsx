const problemCardsData = [
  {
    image: "/images/limited-time.png",
    title: "Limited Time",
    description:
      "Training plans that ignore your schedule don't survive the week.",
  },
  {
    image: "/images/inconsistent-equipment.png",
    title: "Inconsistent Equipment",
    description:
      "Programs break when machines, racks, or barbells aren't available.",
  },
  {
    image: "/images/over-complicated.png",
    title: "Over-complicated Planning",
    description: "Too many rules and spreadsheets—no clear, usable plan.",
  },
];

function ProblemCard({ image, title, description }) {
  return (
    <div className="group relative">
      <div className="absolute inset-0 bg-linear-to-br from-cyan-500/8 to-blue-500/8 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative backdrop-blur-sm bg-white/4 border border-white/10 rounded-3xl p-6 hover:bg-white/8 hover:border-white/20 hover:-translate-y-2 hover:shadow-xl transition-all duration-300">
        <div className="aspect-square bg-white/5 rounded-2xl mb-6 flex items-center justify-center overflow-hidden border border-white/10">
          <img
            src={image}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        </div>
        
        <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

export default function ProblemSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {problemCardsData.map((card, index) => (
        <div
          key={index}
          className="animate-[fadeIn_0.6s_ease-out]"
          style={{ animationDelay: `${index * 0.1}s`, animationFillMode: 'backwards' }}
        >
          <ProblemCard {...card} />
        </div>
      ))}
    </div>
  );
}
