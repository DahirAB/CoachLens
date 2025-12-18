# CoachLens

CoachLens is a constraint-based weekly training planner designed to generate feasible and explainable workout schedules under real-world conditions. Unlike template-driven fitness applications, CoachLens models training as an optimisation problem, accounting for limited availability, recovery requirements, equipment constraints, and user preferences.

Users specify structured constraints such as available time windows, preferred muscle groups, and minimum recovery periods. These inputs are processed by a backend optimisation service, which produces a weekly plan that satisfies all hard constraints while attempting to maximise adherence to soft preferences. When constraints conflict, the system provides clear explanations for trade-offs and infeasible outcomes.

The system is built with a React-based frontend for user interaction and a FastAPI backend that exposes optimisation functionality as a service. CoachLens prioritises clarity, feasibility, and transparency over feature bloat, focusing on the quality and interpretability of generated plans rather than social or commercial fitness features.
