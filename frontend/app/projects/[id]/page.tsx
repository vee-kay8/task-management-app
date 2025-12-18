'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, tasksApi } from '@/lib/api'
import { useParams, useRouter } from 'next/navigation'
import { useState } from 'react'
import { ArrowLeft, Plus, Users, Settings } from 'lucide-react'
import Link from 'next/link'
import TaskBoard from '@/components/TaskBoard'
import CreateTaskModal from '@/components/CreateTaskModal'
import TaskDetailModal from '@/components/TaskDetailModal'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const projectId = params.id as string

  const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<any>(null)

  // Fetch project details
  const { data: projectData, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
  })

  const project = projectData?.project

  // Fetch tasks
  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => tasksApi.list(projectId),
  })

  const tasks = tasksData?.tasks || []

  if (projectLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Project not found</h2>
        <p className="text-gray-600 mb-6">The project you're looking for doesn't exist.</p>
        <Link href="/projects" className="btn btn-primary">
          Back to Projects
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          {/* Back Button */}
          <Link
            href="/projects"
            className="mt-1 p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>

          {/* Project Info */}
          <div>
            <div className="flex items-center space-x-3">
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center text-white text-xl font-bold"
                style={{ backgroundColor: project.color }}
              >
                {project.name.charAt(0)}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                <p className="text-gray-600 mt-1">{project.description}</p>
              </div>
            </div>

            {/* Meta Info */}
            <div className="flex items-center space-x-4 mt-4 text-sm text-gray-600">
              <span className={`badge ${
                project.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                project.status === 'PLANNING' ? 'bg-yellow-100 text-yellow-800' :
                project.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {project.status}
              </span>
              <span className="flex items-center">
                <Users className="w-4 h-4 mr-1" />
                {project.member_count || 1} members
              </span>
              {project.start_date && (
                <span>
                  {new Date(project.start_date).toLocaleDateString()} - {' '}
                  {project.end_date ? new Date(project.end_date).toLocaleDateString() : 'No end date'}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsCreateTaskOpen(true)}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            New Task
          </button>
        </div>
      </div>

      {/* Task Board */}
      {tasksLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <TaskBoard
          tasks={tasks}
          projectId={projectId}
          onTaskClick={(task) => setSelectedTask(task)}
        />
      )}

      {/* Modals */}
      <CreateTaskModal
        isOpen={isCreateTaskOpen}
        onClose={() => setIsCreateTaskOpen(false)}
        projectId={projectId}
        onSuccess={() => {
          setIsCreateTaskOpen(false)
          queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
        }}
      />

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={() => {
            queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
          }}
        />
      )}
    </div>
  )
}
