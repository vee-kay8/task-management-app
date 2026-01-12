/**
 * TypeScript type definitions for the application
 */

// User types
export interface User {
  id: string
  email: string
  username: string
  full_name: string
  role?: string
  created_at: string
  updated_at: string
}

// Project types
export type ProjectStatus = 'PLANNING' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED'

export interface Project {
  id: string
  name: string
  description: string
  status: ProjectStatus
  color: string
  start_date: string
  end_date: string
  created_by: string
  created_at: string
  updated_at: string
  member_count?: number
  task_summary?: {
    TODO: number
    IN_PROGRESS: number
    IN_REVIEW: number
    DONE: number
  }
}

// Task types
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE'
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  project_id: string
  assigned_to?: string
  due_date?: string
  estimated_hours?: number
  actual_hours?: number
  tags?: string
  created_by: string
  created_at: string
  updated_at: string
  assignee?: User
  comments?: Comment[]
}

// Comment types
export interface Comment {
  id: string
  task_id: string
  user_id: string
  content: string
  created_at: string
  updated_at: string
  user: User
}

// API Error types
export interface ApiError {
  response?: {
    data?: {
      error?: string
      message?: string
    }
  }
  message?: string
}
