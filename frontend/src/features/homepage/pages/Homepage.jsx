import { Link } from "react-router-dom";
import ProblemSection from "../components/ProblemCards";
import HowItWorks from "../components/HowItWorks";
import ConstraintsPanel from "../components/ConstraintsPanel";

export default function Homepage() {
  return (
    <div className="min-h-screen bg-linear-to-br from-canvas-deep via-canvas to-canvas-light relative overflow-hidden">
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/5 border-b border-white/10">
        <div className="flex items-center justify-between px-8 py-4 max-w-7xl mx-auto">
          <span className="text-xl font-bold text-white tracking-tight">
            CoachLens
          </span>
          <nav className="flex items-center">
            <Link
              to="/signup"
              className="text-sm font-medium text-white/90 hover:text-white px-5 py-2.5 rounded-full border border-white/20 hover:border-white/40 hover:bg-white/10 transition-all duration-200"
            >
              Sign Up
            </Link>
          </nav>
        </div>
      </header>

      <section className="relative px-8 pt-20 pb-24 max-w-7xl mx-auto">
        <div className="absolute top-1/2 right-1/4 w-[700px] h-[700px] bg-gradient-radial from-cyan-400/8 via-blue-500/6 to-transparent rounded-full blur-[140px] -z-10" />

        <div className="grid lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6 animate-[fadeIn_0.8s_ease-out]">
            <h1 className="text-6xl lg:text-7xl font-bold text-white tracking-tight leading-[1.15] mb-6">
              Optimise Your
              <span className="block bg-linear-to-r from-cyan-400 via-blue-400 to-indigo-500 bg-clip-text text-transparent pb-2 leading-[1.3]">
                Training.
              </span>
            </h1>

            <p className="text-xl text-slate-300 max-w-xl leading-relaxed">
              Constraint-aware training plans, generated automatically around your schedule, equipment, and goals.
            </p>
            <p className="text-sm text-slate-400 font-mono">
              Time + Equipment + Goal → Weekly Plan
            </p>

            <div className="flex flex-col sm:flex-row items-start gap-4 pt-4">
              <Link
                to="/example"
                className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl text-base font-semibold hover:shadow-[0_0_40px_rgba(0,180,255,0.25)] hover:-translate-y-0.5 hover:brightness-110 transition-all duration-300"
              >
                See Example
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 rounded-2xl text-base font-medium text-white border border-white/30 hover:border-white/50 hover:bg-white/10 hover:-translate-y-0.5 transition-all duration-300"
              >
                Login
              </Link>
            </div>
          </div>

          <div className="lg:col-span-5 animate-[fadeIn_1s_ease-out_0.2s_backwards]">
            <ConstraintsPanel />
          </div>
        </div>
      </section>

      <section id="problems" className="relative px-8 py-20 max-w-7xl mx-auto">
        <div className="text-center mb-12 animate-[fadeIn_0.6s_ease-out]">
          <h2 className="text-3xl font-bold text-white mb-3">
            Built for real-world constraints
          </h2>
          <p className="text-slate-400">
            Training plans fail when they ignore reality
          </p>
        </div>
        <ProblemSection />
      </section>

      <section id="how-it-works" className="relative px-8 py-24 max-w-6xl mx-auto">
        <HowItWorks />
      </section>

      <div className="h-20" />
    </div>
  );
}
