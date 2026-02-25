import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

function ProfileErrorUI({ onRetry }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-white text-lg gap-4 bg-canvas">
      <p>Could not load profile. Please refresh or try again.</p>
      <button
        type="button"
        onClick={onRetry}
        className="px-4 py-2 bg-white/20 rounded hover:bg-white/30 transition-colors"
      >
        Retry
      </button>
    </div>
  )
}

export default function ProtectedRoute({ requireOnboarding = false, redirectIfOnboardingComplete = false, children }) {
  const { pathname } = useLocation()
  const { user, profile, loading, profileError, refreshProfile } = useAuth()

  if (profileError) {
    return <ProfileErrorUI onRetry={() => refreshProfile()} />
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white text-lg bg-canvas">
        Loading…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const onboardingDone = profile?.onboarding_completed ?? false

  if (requireOnboarding && (!profile || !onboardingDone)) {
    if (pathname === '/onboarding') return <>{children}</>
    return <Navigate to="/onboarding" replace />
  }

  if (redirectIfOnboardingComplete && onboardingDone) {
    if (pathname === '/app') return <>{children}</>
    return <Navigate to="/app" replace />
  }

  return <>{children}</>
}
