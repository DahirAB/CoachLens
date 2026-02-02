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
    <div className="bg-surface-primary rounded-2xl p-6 ">
      <div className="aspect-square bg-surface-secondary rounded-xl mb-6 flex items-center justify-center overflow-hidden">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover"
        />
      </div>
      <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
      <p className="text-sm text-slate-500  leading-relaxed">{description}</p>
    </div>
  );
}

export default function ProblemSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {problemCardsData.map((card, index) => (
        <ProblemCard key={index} image={card.image} title={card.title} description={card.description}/>
      ))}
    </div>
  );
}
