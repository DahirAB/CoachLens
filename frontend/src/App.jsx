import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import Homepage from "./features/homepage/pages/Homepage";
import ExamplePlanPage from "./features/plans/pages/ExamplePlanPage";
import Login from "./features/auth/pages/Login";
import Signup from "./features/auth/pages/Signup";
import Onboarding from "./features/onboarding/OnboardingPage";
import AppPage from "./features/plans/pages/AppPage";
import TrackingPage from "./features/plans/pages/TrackingPage";
import EditConstraintsPage from "./features/constraints/EditConstraintsPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";
import { PlanProvider } from "./features/plans/context/PlanContext";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="/example" element={<ExamplePlanPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute redirectIfOnboardingComplete>
            <Onboarding />
          </ProtectedRoute>
        }
      />
      <Route
        path="/app"
        element={
          <ProtectedRoute requireOnboarding={true}>
            <PlanProvider>
              <Outlet />
            </PlanProvider>
          </ProtectedRoute>
        }
      >
        <Route index element={<AppPage />} />
        <Route path="track" element={<TrackingPage />} />
        <Route path="constraints" element={<EditConstraintsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
