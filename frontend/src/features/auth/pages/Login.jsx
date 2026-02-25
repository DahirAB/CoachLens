import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import Input from "../components/Input";

export default function Login() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail) return setError("Email is required.");
    if (!password) return setError("Password is required.");

    setSubmitting(true);
    try {
      const { error: supaError } = await signIn({ email: trimmedEmail, password });
      if (supaError) {
        setError(supaError.message);
        return;
      }
      navigate("/app", { replace: true });
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden flex flex-col items-center px-6">
      <Link
        to="/"
        className="absolute top-6 left-8 text-sm font-bold text-white tracking-tight hover:text-cyan-400 transition-colors z-10"
      >
        CoachLens
      </Link>

      <div className="flex-1 flex items-center justify-center w-full pt-16">
        <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] bg-cyan-500/8 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-[100px]" />

        <div className="relative w-full max-w-[420px] animate-[fadeIn_0.6s_ease-out]">
          <div className="absolute inset-0 bg-linear-to-br from-cyan-500/6 to-blue-500/4 rounded-3xl blur-xl" />

          <div className="relative backdrop-blur-lg bg-white/4 border border-white/8 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,150,255,0.08)]">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-white mb-2">Welcome back</h1>
              <p className="text-slate-400 text-sm">
                Log in to continue building smarter plans.
              </p>
            </div>

            {error && (
              <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                id="login-email"
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />

              <Input
                id="login-password"
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-linear-to-r from-cyan-500 to-blue-500 text-white py-3.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
              >
                {submitting ? "Logging in…" : "Login"}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/signup"
                className="block w-full py-3.5 rounded-xl text-sm font-medium text-white border border-white/20 hover:border-white/40 hover:bg-white/6 transition-all duration-200 text-center"
              >
                Create account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
