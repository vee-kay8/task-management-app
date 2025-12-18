'use client'

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '@/lib/api'
import { useState } from 'react'
import Link from 'next/link'
import { Plus, FolderKanban, Search, Filter, Trash2 } from 'lucide-react'
import CreateProjectModal from '@/components/CreateProjectModal'

export default function ProjectsPage() {
  const queryClient = useQueryClient()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Fetch projects
  const { data: projectsData, isLoading, refetch } = useQuery({
    queryKey: ['projects', statusFilter],
    queryFn: async () => {
      // Fetch all projects by requesting a large per_page value
      const result = await projectsApi.list({ 
        status: statusFilter === 'all' ? undefined : statusFilter,
        page: 1
      })
      console.log('Fetched projects:', result)
      return result
    },
  })

  const projects = projectsData?.projects || []

  // Filter projects by search
  const filteredProjects = projects.filter((project: any) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Handle project deletion
  const handleDelete = async (e: React.MouseEvent, projectId: string, projectName: string) => {
    e.preventDefault() // Prevent navigation to project detail
    e.stopPropagation()
    
    const confirmMessage = `Are you sure you want to delete "${projectName}"? This action cannot be undone.`
    if (!confirm(confirmMessage)) {
      return
    }

    setDeletingId(projectId)
    try {
      await projectsApi.delete(projectId)
      // Invalidate cache to refresh the list
      await queryClient.invalidateQueries({ queryKey: ['projects'] })
    } catch (error: any) {
      alert(error.message || 'Failed to delete project')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-gray-600">
            Manage and organize all your projects
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn btn-primary inline-flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Project
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="sm:w-48">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="all">All Status</option>
              <option value="PLANNING">Planning</option>
              <option value="ACTIVE">Active</option>
              <option value="ON_HOLD">On Hold</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="card text-center py-12">
          <FolderKanban className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery ? 'No projects found' : 'No projects yet'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery 
              ? 'Try adjusting your search or filters' 
              : 'Get started by creating your first project!'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn btn-primary inline-flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Project
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project: any) => (
            <div key={project.id} className="relative">
              <Link
                href={`/projects/${project.id}`}
                className="card hover:shadow-lg transition-shadow cursor-pointer group block"
              >
                {/* Project Color Bar */}
                <div 
                  className="h-2 -mx-6 -mt-6 mb-4 rounded-t-lg"
                  style={{ backgroundColor: project.color }}
                />

                {/* Project Info */}
                <div className="space-y-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                        {project.name}
                      </h3>
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                        {project.description || 'No description'}
                      </p>
                    </div>
                    
                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDelete(e, project.id, project.name)}
                      disabled={deletingId === project.id}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      title="Delete project"
                    >
                      {deletingId === project.id ? (
                        <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Trash2 className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Status Badge */}
                <div>
                  <span className={`badge ${
                    project.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                    project.status === 'PLANNING' ? 'bg-yellow-100 text-yellow-800' :
                    project.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                    project.status === 'ON_HOLD' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {project.status}
                  </span>
                </div>

                {/* Task Summary */}
                {project.task_summary && (
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center">
                      <span className="w-2 h-2 rounded-full bg-gray-400 mr-1.5" />
                      {project.task_summary.TODO} Todo
                    </span>
                    <span className="flex items-center">
                      <span className="w-2 h-2 rounded-full bg-blue-400 mr-1.5" />
                      {project.task_summary.IN_PROGRESS} In Progress
                    </span>
                    <span className="flex items-center">
                      <span className="w-2 h-2 rounded-full bg-green-400 mr-1.5" />
                      {project.task_summary.DONE} Done
                    </span>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-500">
                    {project.member_count || 1} members
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(project.created_at).toLocaleDateString()}
                  </div>
                </div>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={async () => {
          console.log('Project created, invalidating cache...')
          setIsCreateModalOpen(false)
          // Invalidate all project queries to force refetch
          await queryClient.invalidateQueries({ queryKey: ['projects'] })
          console.log('Cache invalidated, refetching...')
        }}
      />
    </div>
  )
}
