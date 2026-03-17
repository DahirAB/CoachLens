import { supabase } from './supabaseClient'

const BASE_URL = import.meta.env.VITE_BACKEND_URL

if (!BASE_URL || BASE_URL.startsWith('<')) {
  throw new Error(
    'Missing URL or its invalid.'
  )
}

const _inflight = new Map()
// method that deduplicates get requests done by ai 
export async function backendRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()

  if (method === 'GET') {
    if (_inflight.has(path)) return _inflight.get(path)
    const promise = _rawBackendRequest(path, options).finally(() => {
      _inflight.delete(path)
    })
    _inflight.set(path, promise)
    return promise
  }

  return _rawBackendRequest(path, options)
}

async function _rawBackendRequest(path, options = {}) {
  const { data: { session } } = await supabase.auth.getSession()
  const token = session?.access_token

  if (!token) {
    const err = new Error('Not authenticated')
    err.status = 401
    throw err
  }

  const { body, headers: extraHeaders, ...fetchOptions } = options

  const headers = {
    Authorization: `Bearer ${token}`,
    ...extraHeaders,
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...fetchOptions,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (networkErr) {
    const err = new Error(networkErr?.message || 'Network error')
    err.status = 0
    throw err
  }

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`
    try {
      const err = await response.json()
      const detail = err.detail 
      if (Array.isArray(detail)) {
        message = detail.map((e) => e.msg ?? JSON.stringify(e)).join('; ')
      } else if (detail) {
        message = String(detail)
      }
    } catch {}
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  if (response.status === 204) return null

  return response.json()
}

export async function publicRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  if (method !== 'GET') {
    throw new Error('publicRequest only supports GET')
  }

  const { body, headers: extraHeaders, ...rest } = options
  if (body !== undefined) {
    throw new Error('publicRequest does not support request body (GET only)')
  }

  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...rest,
      method: 'GET',
      headers: { ...extraHeaders },
    })
  } catch (networkErr) {
    const err = new Error(networkErr?.message || 'Network error')
    err.status = 0
    throw err
  }

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`
    try {
      const err = await response.json()
      const detail = err.detail
      if (Array.isArray(detail)) {
        message = detail.map((e) => e.msg ?? JSON.stringify(e)).join('; ')
      } else if (detail) {
        message = String(detail)
      }
    } catch {}
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  if (response.status === 204) return null

  return response.json()
}
