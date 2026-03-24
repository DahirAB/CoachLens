import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { backendRequest } from "../../../api/backendClient";

const PlanContext = createContext(null);

export function PlanProvider({ children }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [noPlan, setNoPlan] = useState(false);
  const [error, setError] = useState("");
  const [viewingOldPlan, setViewingOldPlan] = useState(false);

  const refreshLatestPlan = useCallback(async () => {
    setLoading(true);
    setError("");
    setViewingOldPlan(false);
    try {
      const data = await backendRequest("/api/plans/latest");
      setPlan(data);
      setNoPlan(false);
    } catch (err) {
      if (err.status === 404) {
        setPlan(null);
        setNoPlan(true);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const viewPlan = useCallback(async (planId) => {
    setLoading(true);
    setError("");
    try {
      const data = await backendRequest(`/api/plans/${planId}`);
      setPlan(data);
      setViewingOldPlan(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshLatestPlan();
  }, [refreshLatestPlan]);

  return (
    <PlanContext.Provider value={{ plan, loading, noPlan, error, setError, refreshLatestPlan, viewingOldPlan, viewPlan }}>
      {children}
    </PlanContext.Provider>
  );
}

export function useLatestPlan() {
  const ctx = useContext(PlanContext);
  if (!ctx) throw new Error("useLatestPlan must be inside PlanProvider");
  return ctx;
}
