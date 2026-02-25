import { Routes, Route, Navigate } from "react-router-dom";
import Homepage from "./features/homepage/pages/Homepage";
import ExamplePlanPage from "./features/plans/pages/ExamplePlanPage";
import Login from "./features/auth/pages/Login";
import Signup from "./features/auth/pages/Signup";
import Onboarding from "./features/onboarding/OnboardingPage";
import AppPage from "./features/plans/pages/AppPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="/example" element={<ExamplePlanPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/onboardingj"
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
            <AppPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
