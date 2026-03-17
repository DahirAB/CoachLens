import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { backendRequest, publicRequest } from "../../../api/backendClient";
import { useAuth } from "../AuthContext";
import Input from "../components/Input";

const PASSWORD_MIN_LENGTH = 8;
const USERNAME_ERROR = "Use 3–20 letters,numbers , _ and have at least one digit";

function validatePassword(pwd) {
  if (pwd.length < PASSWORD_MIN_LENGTH) {
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters.`;
  }
  if (!/[a-z]/.test(pwd)) return "Password must include at least one lowercase letter.";
  if (!/[A-Z]/.test(pwd)) return "Password must include at least one uppercase letter.";
  if (!/\d/.test(pwd)) return "Password must include at least one digit.";
  if (!/[^a-zA-Z0-9]/.test(pwd)) return "Password must include at least one symbol (e.g. !@#$%).";
  return null;
}

function validateUsername(username) {
  const u = username.trim().toLowerCase();
  if (!u) return "Username is required.";
  if (u.length < 3 || u.length > 20) return USERNAME_ERROR;
  if (!/^[a-z0-9_]+$/.test(u)) return USERNAME_ERROR;
  if (!/[0-9]/.test(u)) return USERNAME_ERROR;
  return null;
}

export default function Signup() {
  const navigate = useNavigate();
  const { signUp, refreshProfile } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const u = username.trim().toLowerCase();
    const usernameError = validateUsername(username);
    if (usernameError) return setError(usernameError);
    if (!email.trim()) return setError("Email is required.");

    const passwordError = validatePassword(password);
    if (passwordError) return setError(passwordError);
    if (password !== confirmPassword) return setError("Passwords do not match.");

    setSubmitting(true);
    try {
      // check username to stop orphan profiles
      try {
        await publicRequest(`/api/profile/username-available?username=${u}`);
      } catch (err) {
        if (err.status === 409) {
          setError("That username is already taken");
          return;
        }
        if (err.status === 400) {
          setError(err.message || USERNAME_ERROR);
          return;
        }
        throw err;
      }

      const trimmedEmail = email.trim().toLowerCase();
      const { error: supaError } = await signUp({ email: trimmedEmail, password });
      if (supaError) {
        setError(supaError.message);
        return;
      }

      const profile = await backendRequest("/api/profile", {
        method: "PATCH",
        body: { username: u },
      });
      refreshProfile(profile);
      navigate("/onboarding", { replace: true });
    } catch (err) {
      if (err.status === 409) {
        setError("That username is already taken");
      } else if (err.status === 400) {
        setError(err.message || USERNAME_ERROR);
      } else {
        setError("Something went wrong. Please try again.");
      }
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
      

        <div className="relative w-full max-w-[480px] animate-[fadeIn_0.6s_ease-out]">
          <div className="absolute inset-0 bg-linear-to-br from-cyan-500/6 to-blue-500/4 rounded-3xl blur-xl" />

          <div className="relative backdrop-blur-lg bg-white/4 border border-white/8 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,150,255,0.08)]">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-white mb-2">Create your account</h1>
              <p className="text-slate-400 text-sm">
                Set up your profile and generate your first intelligent plan.
              </p>
            </div>

            {error && (
              <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <Input
                  id="signup-username"
                  label="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe1"
                  autoComplete="username"
                  required
                />
                <p className="text-xs text-slate-500 mt-1">
                Use 3–20 letters,numbers , _ and have at least one digit
                </p>
              </div>

              <Input
                id="signup-email"
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />

              <Input
                id="signup-password"
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Choose a password"
                autoComplete="new-password"
                required
                minLength={PASSWORD_MIN_LENGTH}
                passwordWithHint
                hasError={!!error && error.toLowerCase().includes("password")}
              />

              <Input
                id="signup-confirm"
                label="Confirm password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repeat your password"
                autoComplete="new-password"
                required
                minLength={PASSWORD_MIN_LENGTH}
              />

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-linear-to-r from-cyan-500 to-blue-500 text-white py-3.5 rounded-xl text-sm font-semibold hover:shadow-[0_0_30px_rgba(0,180,255,0.25)] hover:brightness-110 transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
              >
                {submitting ? "Creating account…" : "Continue to onboarding"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
              >
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
