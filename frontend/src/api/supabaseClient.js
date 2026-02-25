import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY

if (!supabaseUrl || supabaseUrl.startsWith('<')) {
  throw new Error(
    'Missing VITE_SUPABASE_URL. Add it to frontend/.env.local (see .env.local for placeholders).'
  )
}
if (!supabaseAnonKey || supabaseAnonKey.startsWith('<')) {
  throw new Error(
    'Missing VITE_SUPABASE_PUBLISHABLE_KEY. Add it to frontend/.env.local (see .env.local for placeholders).'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
