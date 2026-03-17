import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../../api/supabaseClient'
import { backendRequest } from '../../api/backendClient'

const AuthContext = createContext(undefined)

async function fetchProfile() {
  try {
    return await backendRequest('/api/profile')
  } catch (err) {
    if (err.status === 404) return null
    throw err
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [profileError, setProfileError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [initialised, setInitialised] = useState(false)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: initial } }) => {
      setSession(initial)
      setUser(initial?.user ?? null)
      setInitialised(true)
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession)
      setUser(newSession?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (!initialised) return

    if (!user) {
      setProfile(null)
      setProfileError(null)
      setLoading(false)
      return
    }

    setProfileError(null)
    setLoading(true)
    let cancelled = false
    fetchProfile()
      .then((p) => {
        if (!cancelled) {
          setProfile(p)
          setProfileError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setProfile(null)
          setProfileError(err)
          setLoading(false)
        }
      })
    return () => { cancelled = true }
  }, [user?.id, initialised])

  async function refreshProfile(updatedProfile = null) {
    if (updatedProfile !== null) {
      setProfile(updatedProfile)
      setProfileError(null)
      return
    }
    if (!user) {
      setProfile(null)
      setProfileError(null)
      return
    }
    try {
      const p = await fetchProfile()
      setProfile(p)
      setProfileError(null)
    } catch (err) {
      setProfile(null)
      setProfileError(err)
    }
  }

  function signUp({ email, password }) {
    return supabase.auth.signUp({ email, password })
  }

  function signIn({ email, password }) {
    return supabase.auth.signInWithPassword({ email, password })
  }

  function signOut() {
    return supabase.auth.signOut()
  }

  const value = {
    session,
    user,
    profile,
    loading,
    profileError,
    signUp,
    signIn,
    signOut,
    refreshProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
