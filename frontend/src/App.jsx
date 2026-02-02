import ProblemSection from "./components/ProblemCards";
import HowItWorks from "./components/HowItWorks";

function App() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        
        <span className="text-surface-primary text-xl font-semibold">
          CoachLens
        </span>

        <nav className="flex items-center">
          <button className="text-slate-300 hover:text-surface-primary transition-colors text-sm" disabled>
            Sign Up
          </button>
        </nav>
      </header>
      {/* top*/}
      <section className="flex flex-col items-center justify-center text-center px-8 py-32 max-w-4xl mx-auto">
        <h1 className="text-5xl md:text-6xl font-bold text-surface-primary mb-4">
          Optimise Your Training.
        </h1>
        <p className="text-xl md:text-2xl text-slate-300 mb-10">
          Constraint-aware training plans, built around you.
        </p>

        
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <button className="bg-amber-500 text-slate-900 px-6 py-3 rounded-full text-sm font-medium hover:bg-amber-600 transition-colors">
            Generate My Plan
          </button>
          <button className="px-6 py-3 rounded-full text-sm font-medium 
           text-surface-primary border border-slate-300
             transition-transform duration-300 hover:-translate-y-0.5">
            See Example
          </button>
        </div>
      </section>

      {/* Problem */}
      <section id="problems" className="px-8 py-16 max-w-6xl mx-auto">
        <ProblemSection />
      </section>

      {/* How It Works*/}
      <section id="how-it-works" className="px-8 py-16 max-w-6xl mx-auto">
        <HowItWorks />
      </section>

      {/*Footer */}
      <div ></div>
    </div>
  );
}

export default App;
