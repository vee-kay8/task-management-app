/**
 * API client functions
 * Mock for testing - replace with actual implementation
 */

export const tasksApi = {
  update: async (taskId: string, data: Partial<Record<string, unknown>>) => {
    // Mock implementation
    return { id: taskId, ...data }
  },
}
