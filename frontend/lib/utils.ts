/**
 * Utility functions for the application
 */

/**
 * Get CSS class for priority badge color
 */
export function getPriorityColor(priority: string): string {
  const colors = {
    URGENT: 'bg-red-100 text-red-800',
    HIGH: 'bg-orange-100 text-orange-800',
    MEDIUM: 'bg-yellow-100 text-yellow-800',
    LOW: 'bg-green-100 text-green-800',
  }
  return colors[priority as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

/**
 * Get CSS class for status badge color
 */
export function getStatusColor(status: string): string {
  const colors = {
    TODO: 'bg-gray-100 text-gray-800',
    IN_PROGRESS: 'bg-blue-100 text-blue-800',
    IN_REVIEW: 'bg-purple-100 text-purple-800',
    DONE: 'bg-green-100 text-green-800',
  }
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

/**
 * Get user initials from username
 */
export function getInitials(username: string): string {
  return username
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Format date to readable string
 */
export function formatDate(dateString: string): string {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 30) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  return formatDate(dateString)
}
