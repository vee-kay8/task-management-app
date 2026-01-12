/**
 * API client functions
 * Mock implementations for testing - replace with actual API calls
 */

import type { User, Project, Task } from './types'

// Mock data for testing
const mockUsers: User[] = []
const mockProjects: Project[] = []
const mockTasks: Task[] = []

// Auth API
export const authApi = {
  login: async (email: string, _password: string) => {
    // Mock implementation
    return {
      user: { id: '1', email, username: email.split('@')[0], full_name: 'Test User', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
    }
  },
  register: async (email: string, username: string, _password: string, full_name: string) => {
    // Mock implementation
    return {
      user: { id: '1', email, username, full_name, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
    }
  },
}

// Projects API
export const projectsApi = {
  list: async (params?: { page?: number; status?: string }) => {
    // Mock implementation with pagination
    const filtered = params?.status && params.status !== 'all' 
      ? mockProjects.filter((p) => p.status === params.status)
      : mockProjects
    return {
      projects: filtered,
      total: filtered.length,
      page: params?.page || 1,
      total_pages: 1,
    }
  },
  getAll: async () => {
    // Mock implementation
    return mockProjects
  },
  get: async (id: string) => {
    // Mock implementation
    return mockProjects.find((p) => p.id === id) || null
  },
  create: async (data: Partial<Project>) => {
    // Mock implementation
    const newProject = { id: Date.now().toString(), ...data } as Project
    mockProjects.push(newProject)
    return newProject
  },
  update: async (id: string, data: Partial<Project>) => {
    // Mock implementation
    const index = mockProjects.findIndex((p) => p.id === id)
    if (index >= 0) {
      mockProjects[index] = { ...mockProjects[index], ...data }
      return mockProjects[index]
    }
    return null
  },
  delete: async (id: string) => {
    // Mock implementation
    const index = mockProjects.findIndex((p) => p.id === id)
    if (index >= 0) {
      mockProjects.splice(index, 1)
    }
  },
}

// Tasks API
export const tasksApi = {
  getByProject: async (projectId: string) => {
    // Mock implementation
    return mockTasks.filter((t) => t.project_id === projectId)
  },
  create: async (data: Partial<Task>) => {
    // Mock implementation
    const newTask = { id: Date.now().toString(), ...data } as Task
    mockTasks.push(newTask)
    return newTask
  },
  update: async (taskId: string, data: Partial<Record<string, unknown>>) => {
    // Mock implementation
    return { id: taskId, ...data }
  },
  delete: async (id: string) => {
    // Mock implementation
    const index = mockTasks.findIndex((t) => t.id === id)
    if (index >= 0) {
      mockTasks.splice(index, 1)
    }
  },
}

// Users API
export const usersApi = {
  getAll: async () => {
    // Mock implementation
    return mockUsers
  },
}

