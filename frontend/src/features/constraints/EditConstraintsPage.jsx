import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { backendRequest, publicRequest } from "../../api/backendClient";
import { useAuth } from "../auth/AuthContext";
import StepOne from "../onboarding/components/StepOne";
import StepTwo from "../onboarding/components/StepTwo";
import StepThreeAdvanced from "../onboarding/components/StepThreeAdvanced";
import { profileToFormState } from "../onboarding/profileToFormState";
import { durationToMinutes, goalToEnum, sortDaysLowercase, toNumber } from "../onboarding/utils";
import { useLatestPlan } from "../plans/context/PlanContext";

function StepIndicator({ current, total }) {
  const progress = (current / total) * 100;

  return (
    <div className="mb-8">
      <p className="text-xs text-slate-400 mb-3">
        Step {current} of {total}
      </p>
      <div className="h-1 w-full bg-white/6 rounded-full overflow-hidden">
        <div
          className="h-full bg-linear-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

export default function EditConstraintsPage() {
  const navigate = useNavigate();
  const { profile, refreshProfile } = useAuth();
  const { refreshLatestPlan } = useLatestPlan();

  const initial = useMemo(() => profileToFormState(profile), [profile]);

  const [step, setStep] = useState(1);
  const [selectedDays, setSelectedDays] = useState(initial.selectedDays);
  const [duration, setDuration] = useState(initial.duration);
  const [goal, setGoal] = useState(initial.goal);
  const [selectedEquipment, setSelectedEquipment] = useState(initial.selectedEquipment);
  const [oneRepMaxes, setOneRepMaxes] = useState(initial.oneRepMaxes);
  const [includeCardio, setIncludeCardio] = useState(initial.includeCardio);
  const [requiredPrimaryLifts, setRequiredPrimaryLifts] = useState(initial.requiredPrimaryLifts);
  const [excludedExercises, setExcludedExercises] = useState(initial.excludedExercises);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [catalog, setCatalog] = useState(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState(null);

  useEffect(() => {
    setSelectedDays(initial.selectedDays);
    setDuration(initial.duration);
    setGoal(initial.goal);
    setSelectedEquipment(initial.selectedEquipment);
    setOneRepMaxes(initial.oneRepMaxes);
    setIncludeCardio(initial.includeCardio);
    setRequiredPrimaryLifts(initial.requiredPrimaryLifts);
    setExcludedExercises(initial.excludedExercises);
  }, [initial]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await publicRequest("/api/profile/exercise-catalog");
        if (!cancelled) setCatalog(data);
      } catch (err) {
        if (!cancelled) setCatalogError(err.message);
      } finally {
        if (!cancelled) setCatalogLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  function toggleDay(day) {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day],
    );
  }

  function toggleEquipment(item) {
    setSelectedEquipment((prev) =>
      prev.includes(item) ? prev.filter((e) => e !== item) : [...prev, item],
    );
  }

  function setOneRepMax(lift, value) {
    setOneRepMaxes((prev) => ({ ...prev, [lift]: value }));
  }

  function toggleRequiredLift(liftId) {
    setRequiredPrimaryLifts((prev) =>
      prev.includes(liftId) ? prev.filter((l) => l !== liftId) : [...prev, liftId],
    );
  }

  function toggleExcludedExercise(exId) {
    setExcludedExercises((prev) =>
      prev.includes(exId) ? prev.filter((e) => e !== exId) : [...prev, exId],
    );
  }

  function buildPayload() {
    const squat = toNumber(oneRepMaxes.squat);
    const bench = toNumber(oneRepMaxes.bench);
    const deadlift = toNumber(oneRepMaxes.deadlift);
    const ohp = toNumber(oneRepMaxes.ohp);

    return {
      training_goal: goalToEnum(goal),
      available_days: sortDaysLowercase(selectedDays),
      session_duration_min: durationToMinutes(duration),
      equipment: selectedEquipment.map((e) => e.toLowerCase()),
      include_cardio: includeCardio,
      squat_1rm: squat,
      bench_1rm: bench,
      deadlift_1rm: deadlift,
      ohp_1rm: ohp,
      required_primary_lifts: requiredPrimaryLifts,
      excluded_exercises: excludedExercises,
    };
  }

  function validate() {
    if (selectedDays.length < 1) {
      return { valid: false, stepToFocus: 1, message: "Select at least one training day." };
    }
    if (!duration || !goal) {
      return { valid: false, stepToFocus: 1, message: "Please complete all required fields in step 1." };
    }

    const squat = toNumber(oneRepMaxes.squat);
    const bench = toNumber(oneRepMaxes.bench);
    const deadlift = toNumber(oneRepMaxes.deadlift);
    const ohp = toNumber(oneRepMaxes.ohp);
    if (squat == null || squat <= 0 || bench == null || bench <= 0 || deadlift == null || deadlift <= 0 || ohp == null || ohp <= 0) {
      return {
        valid: false,
        stepToFocus: 2,
        message: "All four one-rep maxes are required (Squat, Bench, Deadlift, OHP).",
      };
    }

    return { valid: true };
  }

  async function submitConstraints({ regenerate }) {
    setError("");
    const validation = validate();
    if (!validation.valid) {
      setStep(validation.stepToFocus);
      setError(validation.message);
      return;
    }

    setSubmitting(true);
    try {
      const updatedProfile = await backendRequest("/api/profile/onboarding", {
        method: "PATCH",
        body: buildPayload(),
      });
      await refreshProfile(updatedProfile);

      if (regenerate) {
        await backendRequest("/api/plans/generate", { method: "POST" });
        await refreshLatestPlan();
      }

      navigate("/app");
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const isLastStep = step === 3;

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden flex flex-col items-center px-6 py-12">
      <Link
        to="/app"
        className="absolute top-6 left-8 text-sm font-bold text-white tracking-tight hover:text-cyan-400 transition-colors z-10"
      >
        CoachLens
      </Link>

      <div className="flex-1 flex items-center justify-center w-full pt-16">
        <div className="absolute top-1/4 left-1/2 w-[600px] h-[600px] bg-cyan-500/6 rounded-full blur-[140px]" />

        <div className="relative w-full max-w-[600px] animate-[fadeIn_0.6s_ease-out]">
          <div className="absolute inset-0 bg-linear-to-br from-cyan-500/6 to-blue-500/4 rounded-3xl blur-xl" />

          <div className="relative backdrop-blur-lg bg-white/4 border border-white/8 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,150,255,0.08)]">
            <StepIndicator current={step} total={3} />

            {error && (
              <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            {step === 1 && (
              <StepOne
                selectedDays={selectedDays}
                toggleDay={toggleDay}
                duration={duration}
                setDuration={setDuration}
                goal={goal}
                setGoal={setGoal}
              />
            )}

            {step === 2 && (
              <StepTwo
                selectedEquipment={selectedEquipment}
                toggleEquipment={toggleEquipment}
                oneRepMaxes={oneRepMaxes}
                setOneRepMax={setOneRepMax}
                includeCardio={includeCardio}
                setIncludeCardio={setIncludeCardio}
              />
            )}

            {step === 3 && (
              <StepThreeAdvanced
                catalog={catalog}
                loading={catalogLoading}
                error={catalogError}
                requiredPrimaryLifts={requiredPrimaryLifts}
                toggleRequiredLift={toggleRequiredLift}
                excludedExercises={excludedExercises}
                toggleExcludedExercise={toggleExcludedExercise}
                selectedEquipment={selectedEquipment}
                includeCardio={includeCardio}
              />
            )}

            <div className="flex gap-4 mt-8">
              {step > 1 && (
                <button
                  type="button"
                  disabled={submitting}
                  onClick={() => setStep(step - 1)}
                  className="flex-1 py-3.5 rounded-xl text-sm font-medium text-white border border-white/20 hover:border-white/40 hover:bg-white/6 transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none"
                >
                  Back
                </button>
              )}

              {!isLastStep && (
                <button
                  type="button"
                  disabled={submitting}
                  onClick={() => setStep(step + 1)}
                  className={`${step > 1 ? "flex-1" : "w-full"} bg-linear-to-r from-cyan-500 to-blue-500 text-white py-3.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none`}
                >
                  Next
                </button>
              )}

              {isLastStep && (
                <>
                  <button
                    type="button"
                    disabled={submitting}
                    onClick={() => submitConstraints({ regenerate: false })}
                    className="flex-1 py-3.5 rounded-xl text-sm font-medium text-white border border-white/20 hover:border-white/40 hover:bg-white/6 transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {submitting ? "Saving..." : "Save constraints"}
                  </button>
                  <button
                    type="button"
                    disabled={submitting}
                    onClick={() => submitConstraints({ regenerate: true })}
                    className="flex-1 bg-linear-to-r from-cyan-500 to-blue-500 text-white py-3.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {submitting ? "Saving..." : "Save & regenerate"}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
