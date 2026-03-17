import { Link } from "react-router-dom";
import DayCard from "../components/DayCard";
import RestDayCard from "../components/RestDayCard";
import { buildRenderDays } from "../utils/weekRendering";

const EXAMPLE_REQUEST = {
  equipment: ["barbell", "dumbbell", "machine"],
  one_rep_maxes: {
    ohp_1rm: 50,
    bench_1rm: 80,
    squat_1rm: 100,
    deadlift_1rm: 120,
  },
  training_goal: "strength",
  available_days: ["monday", "wednesday", "friday"],
  include_cardio: false,
  excluded_exercises: [],
  required_primary_lifts: [],
  session_duration_minutes: 60,
};

const EXAMPLE_PLAN_RESPONSE = {
  week_plan: {
    friday: [
      { name: "Barbell Back Squat", sets: 5, equipment: "barbell", rep_range: "2-5", muscle_group: "legs", rest_minutes: 4, work_minutes: 2, weight_display: null, weight_range_kg: { max: 82, min: 75 } },
      { name: "Dumbbell Lunges", sets: 2, equipment: "dumbbell", rep_range: "8-12", muscle_group: "legs", rest_minutes: 2, work_minutes: 2, weight_display: null, weight_range_kg: null },
      { name: "Leg Extension", sets: 3, equipment: "machine", rep_range: "10-15", muscle_group: "legs", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
      { name: "Barbell Calf Raises", sets: 2, equipment: "barbell", rep_range: "8-12", muscle_group: "legs", rest_minutes: 2, work_minutes: 2, weight_display: null, weight_range_kg: null },
      { name: "Dumbbell Bicep Curl", sets: 3, equipment: "dumbbell", rep_range: "10-15", muscle_group: "arms", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
      { name: "Plank", sets: 4, equipment: "bodyweight", rep_range: "30-60s", muscle_group: "core", rest_minutes: 1, work_minutes: 2, weight_display: null, weight_range_kg: null },
    ],
    monday: [
      { name: "Barbell Bench Press", sets: 5, equipment: "barbell", rep_range: "2-5", muscle_group: "chest", rest_minutes: 4, work_minutes: 2, weight_display: null, weight_range_kg: { max: 66, min: 60 } },
      { name: "Barbell Incline Bench Press", sets: 3, equipment: "barbell", rep_range: "3-5", muscle_group: "chest", rest_minutes: 3, work_minutes: 2, weight_display: null, weight_range_kg: null },
      { name: "Dumbbell Flyes", sets: 3, equipment: "dumbbell", rep_range: "10-15", muscle_group: "chest", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
      { name: "Overhead Press", sets: 3, equipment: "barbell", rep_range: "2-5", muscle_group: "shoulders", rest_minutes: 4, work_minutes: 2, weight_display: null, weight_range_kg: { max: 41, min: 38 } },
      { name: "Rear Delt Flyes", sets: 2, equipment: "machine", rep_range: "10-15", muscle_group: "shoulders", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
    ],
    wednesday: [
      { name: "Leg Curl", sets: 3, equipment: "machine", rep_range: "10-15", muscle_group: "legs", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
      { name: "Dumbbell Deadlift", sets: 5, equipment: "dumbbell", rep_range: "2-5", muscle_group: "back", rest_minutes: 4, work_minutes: 2, weight_display: "38-42 kg per dumbbell ", weight_range_kg: { max: 42, min: 38 } },
      { name: "One-Arm Dumbbell Row", sets: 3, equipment: "dumbbell", rep_range: "3-5", muscle_group: "back", rest_minutes: 3, work_minutes: 2, weight_display: null, weight_range_kg: null },
      { name: "Pullups", sets: 3, equipment: "bodyweight", rep_range: "3-5", muscle_group: "back", rest_minutes: 3, work_minutes: 2, weight_display: null, weight_range_kg: null },
      { name: "Tricep Pushdown", sets: 3, equipment: "machine", rep_range: "10-15", muscle_group: "arms", rest_minutes: 1, work_minutes: 1, weight_display: null, weight_range_kg: null },
    ],
  },
  training_goal: "strength",
  inferred_split: {
    friday: "legs",
    monday: "push",
    wednesday: "pull",
  },
};

const DAY_LABELS = { monday: "Mon", wednesday: "Wed", friday: "Fri" };

export default function ExamplePlanPage() {
  const weekPlan = EXAMPLE_PLAN_RESPONSE.week_plan;
  const inferredSplit = EXAMPLE_PLAN_RESPONSE.inferred_split;
  const req = EXAMPLE_REQUEST;
  const renderDays = buildRenderDays(weekPlan);

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <header className="flex items-center justify-between px-8 py-5">
        <span className="text-sm font-bold text-white tracking-tight">CoachLens</span>
        <Link
          to="/"
          className="text-xs text-slate-400 hover:text-white border border-white/10 hover:border-white/30 rounded-lg px-3 py-1.5 transition-all duration-200"
        >
          Back to home
        </Link>
      </header>

      <main className="max-w-5xl mx-auto px-6 pb-16 space-y-10">
        <h1 className="text-2xl font-bold text-white">Example Plan</h1>

        <section className="backdrop-blur-lg bg-white/4 border border-white/8 rounded-2xl p-6">
          <h2 className="text-base font-semibold text-white mb-4">Constraints that produced this plan</h2>
          <div className="grid sm:grid-cols-2 gap-6 text-sm">
            <div>
              <p className="text-slate-400 mb-1">Training goal</p>
              <p className="text-slate-200 capitalize">{req.training_goal.replace("_", " ")}</p>
            </div>
            <div>
              <p className="text-slate-400 mb-1">Days</p>
              <p className="text-slate-200">
                {req.available_days.map((d) => DAY_LABELS[d] ?? d).join(", ")}
              </p>
            </div>
            <div>
              <p className="text-slate-400 mb-1">Session length</p>
              <p className="text-slate-200">{req.session_duration_minutes} min</p>
            </div>
            <div>
              <p className="text-slate-400 mb-1">Equipment</p>
              <p className="text-slate-200 capitalize">
                {req.equipment.join(", ")}
              </p>
            </div>
            <div>
              <p className="text-slate-400 mb-1">1RMs (kg)</p>
              <p className="text-slate-200">
                Squat {req.one_rep_maxes.squat_1rm}, Bench {req.one_rep_maxes.bench_1rm}, Deadlift {req.one_rep_maxes.deadlift_1rm}, OHP {req.one_rep_maxes.ohp_1rm}
              </p>
            </div>
            <div>
              <p className="text-slate-400 mb-1">Include cardio</p>
              <p className="text-slate-200">{req.include_cardio ? "Yes" : "No"}</p>
            </div>
            {req.excluded_exercises?.length > 0 && (
              <div>
                <p className="text-slate-400 mb-1">Excluded exercises</p>
                <p className="text-slate-200">{req.excluded_exercises.join(", ")}</p>
              </div>
            )}
            {req.required_primary_lifts?.length > 0 && (
              <div>
                <p className="text-slate-400 mb-1">Required primary lifts</p>
                <p className="text-slate-200">{req.required_primary_lifts.join(", ")}</p>
              </div>
            )}
          </div>
        </section>

        <section>
          <h2 className="text-base font-semibold text-white mb-4">Weekly plan</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {renderDays.map((item) =>
              item.type === "workout" ? (
                <DayCard
                  key={item.day}
                  day={item.day}
                  split={inferredSplit?.[item.day]}
                  exercises={item.exercises}
                />
              ) : (
                <RestDayCard key={item.day} day={item.day} />
              )
            )}
          </div>
        </section>

        <div className="flex justify-center">
          <Link
            to="/signup"
            className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl text-base font-semibold hover:shadow-[0_0_40px_rgba(0,180,255,0.25)] hover:-translate-y-0.5 hover:brightness-110 transition-all duration-300"
          >
            Create your own plan
          </Link>
        </div>
      </main>
    </div>
  );
}
