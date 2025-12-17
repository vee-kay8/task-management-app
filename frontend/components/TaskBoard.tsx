'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksApi } from '@/lib/api'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { MoreVertical, Clock, AlertCircle } from 'lucide-react'
import { getPriorityColor, getInitials } from '@/lib/utils'

interface TaskBoardProps {
  tasks: any[]
  projectId: string
  onTaskClick: (task: any) => void
}

const COLUMNS = [
  { id: 'TODO', title: 'To Do', color: 'bg-gray-100' },
  { id: 'IN_PROGRESS', title: 'In Progress', color: 'bg-blue-100' },
  { id: 'IN_REVIEW', title: 'In Review', color: 'bg-purple-100' },
  { id: 'DONE', title: 'Done', color: 'bg-green-100' },
]

export default function TaskBoard({ tasks, projectId, onTaskClick }: TaskBoardProps) {
  const queryClient = useQueryClient()

  // Group tasks by status
  const tasksByStatus = COLUMNS.reduce((acc, column) => {
    acc[column.id] = tasks.filter((task) => task.status === column.id)
    return acc
  }, {} as Record<string, any[]>)

  // Update task status when dragged
  const updateTaskStatus = useMutation({
    mutationFn: ({ taskId, status }: { taskId: string; status: string }) =>
      tasksApi.update(taskId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
    },
  })

  const handleDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result

    // Dropped outside
    if (!destination) return

    // Dropped in same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return
    }

    // Update task status
    const newStatus = destination.droppableId
    updateTaskStatus.mutate({ taskId: draggableId, status: newStatus })
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {COLUMNS.map((column) => (
          <div key={column.id} className="flex flex-col">
            {/* Column Header */}
            <div className={`${column.color} rounded-t-lg px-4 py-3`}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">
                  {column.title}
                </h3>
                <span className="text-sm text-gray-600 bg-white px-2 py-0.5 rounded-full">
                  {tasksByStatus[column.id]?.length || 0}
                </span>
              </div>
            </div>

            {/* Task Cards */}
            <Droppable droppableId={column.id}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`flex-1 bg-gray-50 rounded-b-lg p-3 min-h-[200px] space-y-3 ${
                    snapshot.isDraggingOver ? 'bg-primary-50' : ''
                  }`}
                >
                  {tasksByStatus[column.id]?.map((task, index) => (
                    <Draggable
                      key={task.id}
                      draggableId={task.id}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          onClick={() => onTaskClick(task)}
                          className={`bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow ${
                            snapshot.isDragging ? 'shadow-lg rotate-2' : ''
                          }`}
                        >
                          {/* Priority Badge */}
                          <div className="flex items-start justify-between mb-2">
                            <span className={`badge text-xs ${getPriorityColor(task.priority)}`}>
                              {task.priority}
                            </span>
                          </div>

                          {/* Task Title */}
                          <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
                            {task.title}
                          </h4>

                          {/* Task Meta */}
                          <div className="space-y-2">
                            {/* Due Date */}
                            {task.due_date && (
                              <div className="flex items-center text-xs text-gray-600">
                                <Clock className="w-3 h-3 mr-1" />
                                {new Date(task.due_date).toLocaleDateString()}
                              </div>
                            )}

                            {/* Tags */}
                            {task.tags && task.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {task.tags.slice(0, 2).map((tag: string) => (
                                  <span
                                    key={tag}
                                    className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {task.tags.length > 2 && (
                                  <span className="text-xs text-gray-500">
                                    +{task.tags.length - 2}
                                  </span>
                                )}
                              </div>
                            )}

                            {/* Assignee */}
                            {task.assignee && (
                              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                                <div className="flex items-center space-x-2">
                                  <div className="w-6 h-6 rounded-full bg-primary-600 flex items-center justify-center text-white text-xs font-medium">
                                    {getInitials(task.assignee.full_name)}
                                  </div>
                                  <span className="text-xs text-gray-600">
                                    {task.assignee.full_name.split(' ')[0]}
                                  </span>
                                </div>
                                {task.estimated_hours && (
                                  <span className="text-xs text-gray-500">
                                    {task.estimated_hours}h
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}

                  {/* Empty State */}
                  {tasksByStatus[column.id]?.length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                      <p className="text-sm">No tasks</p>
                    </div>
                  )}
                </div>
              )}
            </Droppable>
          </div>
        ))}
      </div>
    </DragDropContext>
  )
}
