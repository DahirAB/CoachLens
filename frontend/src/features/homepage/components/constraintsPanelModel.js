export const constraintsPanelModel = {
  title: "Constraint categories",

  Tags: [
    "Training days",
    "Session length",
    "Available equipment",
    "Training goal",
    "Main lift focus",
    "Exercise exclusions",
    "Program split",
  ],

  mustSatisfy: [
    { label: "Fits within your time limit" },
    { label: "Includes key compound lifts" },
    { label: "Builds the right split for your schedule" },
    { label: "Movement balance" },
    { label: "Avoids duplicate movement patterns" },
  ],

  optimisesFor: [
    { label: "Appropriate weekly training volume" },
    { label: "High training stimulus" },
    { label: "Exercise variety across the week" },
    { label: "Balanced accessory coverage" },
    { label: "Quality over fillers" },
  ],
};
