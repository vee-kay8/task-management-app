/**
 * API client functions
 * Real API implementation for AWS backend
 */

import type { Project, Task } from './types'

// API base URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

// Helper function to get auth token
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

// Helper function to make authenticated requests
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = getAuthToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Merge with any additional headers from options
  if (options.headers) {
    Object.assign(headers, options.headers)
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }))
    throw new Error(error.error || error.message || 'Request failed')
  }

  return response.json()
}

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Login failed' }))
      throw new Error(error.error || error.message || 'Login failed')
    }

    const data = await response.json()
    
    // Store tokens
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
    }

    return data
  },

  register: async (
    email: string,
    username: string,
    password: string,
    full_name: string
  ) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password, full_name }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Registration failed' }))
      throw new Error(error.error || error.message || 'Registration failed')
    }

    const data = await response.json()
    
    // Store tokens
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
    }

    return data
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },
}

// Projects API
export const projectsApi = {
  list: async (params?: { page?: number; status?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.status && params.status !== 'all') queryParams.append('status', params.status)
    
    const url = `${API_URL}/api/projects${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    return fetchWithAuth(url)
  },

  getAll: async () => {
    return fetchWithAuth(`${API_URL}/api/projects`)
  },

  get: async (id: string) => {
    return fetchWithAuth(`${API_URL}/api/projects/${id}`)
  },

  create: async (data: Partial<Project>) => {
    return fetchWithAuth(`${API_URL}/api/projects`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  update: async (id: string, data: Partial<Project>) => {
    return fetchWithAuth(`${API_URL}/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  delete: async (id: string) => {
    return fetchWithAuth(`${API_URL}/api/projects/${id}`, {
      method: 'DELETE',
    })
  },
}

// Tasks API
export const tasksApi = {
  getByProject: async (projectId: string) => {
    return fetchWithAuth(`${API_URL}/api/projects/${projectId}/tasks`)
  },

  get: async (taskId: string) => {
    return fetchWithAuth(`${API_URL}/api/tasks/${taskId}`)
  },

  create: async (data: Partial<Task>) => {
    return fetchWithAuth(`${API_URL}/api/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  update: async (taskId: string, data: Partial<Record<string, unknown>>) => {
    return fetchWithAuth(`${API_URL}/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  delete: async (id: string) => {
    return fetchWithAuth(`${API_URL}/api/tasks/${id}`, {
      method: 'DELETE',
    })
  },

  addComment: async (taskId: string, content: string) => {
    return fetchWithAuth(`${API_URL}/api/tasks/${taskId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    })
  },
}

// Users API
export const usersApi = {
  getAll: async () => {
    return fetchWithAuth(`${API_URL}/api/users`)
  },

  list: async () => {
    return fetchWithAuth(`${API_URL}/api/users`)
  },
}
