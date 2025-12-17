'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksApi } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { X, Calendar, Clock, User, Tag, MessageSquare, Send } from 'lucide-react'
import { formatDate, formatRelativeTime, getPriorityColor, getStatusColor, getInitials } from '@/lib/utils'

interface TaskDetailModalProps {
  task: any
  onClose: () => void
  onUpdate: () => void
}

export default function TaskDetailModal({ task: initialTask, onClose, onUpdate }: TaskDetailModalProps) {
  const queryClient = useQueryClient()
  const currentUser = useAuthStore((state) => state.user)
  const [commentContent, setCommentContent] = useState('')

  // Fetch full task details with comments
  const { data: task, isLoading } = useQuery({
    queryKey: ['task', initialTask.id],
    queryFn: () => tasksApi.getById(initialTask.id),
    initialData: initialTask,
  })

  // Add comment mutation
  const addComment = useMutation({
    mutationFn: (content: string) => tasksApi.addComment(task.id, content),
    onSuccess: () => {
      setCommentContent('')
      queryClient.invalidateQueries({ queryKey: ['task', task.id] })
      onUpdate()
    },
  })

  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (commentContent.trim()) {
      addComment.mutate(commentContent)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-200 sticky top-0 bg-white z-10">
          <div className="flex-1 pr-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className={`badge ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
              <span className={`badge ${getStatusColor(task.status)}`}>
                {task.status.replace('_', ' ')}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">{task.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
                <p className="text-gray-900 whitespace-pre-wrap">
                  {task.description || 'No description provided'}
                </p>
              </div>

              {/* Comments */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-4 flex items-center">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Comments ({task.comments?.length || 0})
                </h3>

                {/* Add Comment Form */}
                <form onSubmit={handleAddComment} className="mb-6">
                  <div className="flex space-x-3">
                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                      {getInitials(currentUser?.full_name || 'U')}
                    </div>
                    <div className="flex-1">
                      <textarea
                        value={commentContent}
                        onChange={(e) => setCommentContent(e.target.value)}
                        placeholder="Add a comment..."
                        rows={2}
                        className="input resize-none"
                      />
                      <div className="flex justify-end mt-2">
                        <button
                          type="submit"
                          disabled={!commentContent.trim() || addComment.isPending}
                          className="btn btn-primary btn-sm inline-flex items-center"
                        >
                          <Send className="w-4 h-4 mr-1" />
                          {addComment.isPending ? 'Sending...' : 'Comment'}
                        </button>
                      </div>
                    </div>
                  </div>
                </form>

                {/* Comments List */}
                <div className="space-y-4">
                  {task.comments && task.comments.length > 0 ? (
                    task.comments.map((comment: any) => (
                      <div key={comment.id} className="flex space-x-3">
                        <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-700 text-sm font-medium flex-shrink-0">
                          {getInitials(comment.user.full_name)}
                        </div>
                        <div className="flex-1">
                          <div className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-sm text-gray-900">
                                {comment.user.full_name}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatRelativeTime(comment.created_at)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 whitespace-pre-wrap">
                              {comment.content}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-center text-gray-500 text-sm py-4">
                      No comments yet. Be the first to comment!
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Assignee */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                  <User className="w-4 h-4 mr-2" />
                  Assignee
                </h3>
                {task.assignee ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-medium">
                      {getInitials(task.assignee.full_name)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{task.assignee.full_name}</p>
                      <p className="text-xs text-gray-500">{task.assignee.email}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Unassigned</p>
                )}
              </div>

              {/* Reporter */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Reporter</h3>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-700 text-sm font-medium">
                    {getInitials(task.reporter.full_name)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{task.reporter.full_name}</p>
                    <p className="text-xs text-gray-500">{task.reporter.email}</p>
                  </div>
                </div>
              </div>

              {/* Due Date */}
              {task.due_date && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    Due Date
                  </h3>
                  <p className="text-sm text-gray-900">{formatDate(task.due_date)}</p>
                </div>
              )}

              {/* Time Tracking */}
              {(task.estimated_hours || task.actual_hours) && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    Time Tracking
                  </h3>
                  <div className="space-y-1 text-sm">
                    {task.estimated_hours && (
                      <p className="text-gray-900">Estimated: {task.estimated_hours}h</p>
                    )}
                    {task.actual_hours && (
                      <p className="text-gray-900">Actual: {task.actual_hours}h</p>
                    )}
                  </div>
                </div>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                    <Tag className="w-4 h-4 mr-2" />
                    Tags
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {task.tags.map((tag: string) => (
                      <span
                        key={tag}
                        className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Dates */}
              <div className="pt-4 border-t border-gray-200">
                <div className="space-y-2 text-xs text-gray-500">
                  <p>Created {formatRelativeTime(task.created_at)}</p>
                  {task.updated_at && (
                    <p>Updated {formatRelativeTime(task.updated_at)}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
