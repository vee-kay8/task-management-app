'use client'

import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '@/lib/api'
import { useState } from 'react'
import Link from 'next/link'
import { Plus, FolderKanban, Search, Filter } from 'lucide-react'
import CreateProjectModal from '@/components/CreateProjectModal'

export default function ProjectsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // Fetch projects
  const { data: projectsData, isLoading, refetch } = useQuery({
    queryKey: ['projects', statusFilter],
    queryFn: () => projectsApi.getAll({ 
      status: statusFilter === 'all' ? undefined : statusFilter 
    }),
  })

  const projects = projectsData?.projects || []

  // Filter projects by search
  const filteredProjects = projects.filter((project: any) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="card hover:shadow-lg transition-shadow cursor-pointer group"
            >
              {/* Project Color Bar */}
              <div 
                className="h-2 -mx-6 -mt-6 mb-4 rounded-t-lg"
                style={{ backgroundColor: project.color }}
              />

              {/* Project Info */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {project.name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                    {project.description || 'No description'}
                  </p>
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
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          setIsCreateModalOpen(false)
          refetch()
        }}
      />
    </div>
  )
}
