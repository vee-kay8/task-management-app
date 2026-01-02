'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { tasksApi, usersApi } from '@/lib/api'
import { X } from 'lucide-react'

interface CreateTaskModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: string
  onSuccess: () => void
}

export default function CreateTaskModal({ isOpen, onClose, projectId, onSuccess }: CreateTaskModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'TODO',
    priority: 'MEDIUM',
    assigned_to_id: '',
    due_date: '',
    estimated_hours: '',
    tags: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Fetch team members for assignment
  const { data: usersData } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list(),
    enabled: isOpen,
  })

  const users = usersData?.users || []

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const taskData = {
        project_id: projectId,
        title: formData.title,
        description: formData.description || undefined,
        status: formData.status,
        priority: formData.priority,
        assigned_to_id: formData.assigned_to_id || undefined,
        due_date: formData.due_date || undefined,
        estimated_hours: formData.estimated_hours ? Number(formData.estimated_hours) : undefined,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
      }

      await tasksApi.create(taskData)
      onSuccess()
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        status: 'TODO',
        priority: 'MEDIUM',
        assigned_to_id: '',
        due_date: '',
        estimated_hours: '',
        tags: '',
      })
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create task')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white">
          <h2 className="text-xl font-bold text-gray-900">Create New Task</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Task Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Task Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input"
              placeholder="Design homepage mockup"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
              placeholder="Detailed description of the task..."
            />
          </div>

          {/* Status and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="input"
              >
                <option value="TODO">To Do</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="IN_REVIEW">In Review</option>
                <option value="DONE">Done</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="input"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent</option>
              </select>
            </div>
          </div>

          {/* Assignee */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assign To
            </label>
            <select
              value={formData.assigned_to_id}
              onChange={(e) => setFormData({ ...formData, assigned_to_id: e.target.value })}
              className="input"
            >
              <option value="">Unassigned</option>
              {users.map((user: any) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
          </div>

          {/* Due Date and Estimated Hours */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estimated Hours
              </label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={formData.estimated_hours}
                onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                className="input"
                placeholder="8"
              />
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              className="input"
              placeholder="design, ui, frontend"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary flex-1"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={isLoading}
            >
              {isLoading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
