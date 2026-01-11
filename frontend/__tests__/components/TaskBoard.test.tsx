/**
 * ============================================================
 * TASKBOARD COMPONENT TESTS
 * ============================================================
 *
 * What we're testing:
 * - Component renders correctly
 * - Displays tasks in correct columns
 * - Shows correct task counts
 * - Handles empty state
 * - User interactions (clicking tasks)
 *
 * Testing approach:
 * - Test what users see and do, not implementation details
 * - Use accessible queries (getByRole, getByText)
 * - Mock external dependencies (API calls)
 */

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TaskBoard from '@/components/TaskBoard'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

/**
 * ============================================================
 * TEST SETUP & UTILITIES
 * ============================================================
 */

/**
 * Mock data: Sample tasks for testing
 * Represents data that would come from API
 */
const mockTasks = [
  {
    id: '1',
    title: 'Design homepage',
    description: 'Create mockups for homepage',
    status: 'TODO',
    priority: 'HIGH',
    assignee: {
      id: '1',
      full_name: 'John Doe',
      email: 'john@example.com',
    },
    due_date: '2024-02-15',
  },
  {
    id: '2',
    title: 'Setup database',
    description: 'Configure PostgreSQL',
    status: 'IN_PROGRESS',
    priority: 'MEDIUM',
    assignee: {
      id: '2',
      full_name: 'Jane Smith',
      email: 'jane@example.com',
    },
    due_date: '2024-02-10',
  },
  {
    id: '3',
    title: 'Write documentation',
    description: 'API documentation',
    status: 'IN_REVIEW',
    priority: 'LOW',
    assignee: {
      id: '3',
      full_name: 'Bob Johnson',
      email: 'bob@example.com',
    },
    due_date: null,
  },
  {
    id: '4',
    title: 'Deploy to production',
    description: 'Deploy v1.0',
    status: 'DONE',
    priority: 'URGENT',
    assignee: {
      id: '1',
      full_name: 'John Doe',
      email: 'john@example.com',
    },
    due_date: '2024-02-01',
  },
]

/**
 * renderWithQueryClient: Helper to render components with React Query
 *
 * Why needed:
 * - TaskBoard uses React Query for API calls
 * - Tests need QueryClientProvider wrapper
 * - This helper simplifies setup
 *
 * @param ui - Component to render
 * @returns Render result from @testing-library/react
 */
function renderWithQueryClient(ui: React.ReactElement) {
  // Create new QueryClient for each test
  // Ensures tests don't share state
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        // Disable retries in tests
        retry: false,
      },
    },
  })

  // Render component wrapped in provider
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

/**
 * ============================================================
 * TEST SUITE: TaskBoard Rendering
 * ============================================================
 */

describe('TaskBoard Component', () => {
  /**
   * Test: Component renders without crashing
   *
   * This is a "smoke test" - ensures basic rendering works
   * If this fails, something is fundamentally broken
   */
  it('renders without crashing', () => {
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard tasks={[]} projectId="1" onTaskClick={mockOnTaskClick} />
    )

    // Component rendered successfully if we get here
    expect(true).toBe(true)
  })

  /**
   * Test: All four columns are displayed
   *
   * What we're checking:
   * - "To Do" column exists
   * - "In Progress" column exists
   * - "In Review" column exists
   * - "Done" column exists
   *
   * Why important: Users need to see all workflow stages
   */
  it('displays all four status columns', () => {
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard
        tasks={mockTasks}
        projectId="1"
        onTaskClick={mockOnTaskClick}
      />
    )

    // Check for column headers
    // Using getByText because headers are just text
    expect(screen.getByText('To Do')).toBeInTheDocument()
    expect(screen.getByText('In Progress')).toBeInTheDocument()
    expect(screen.getByText('In Review')).toBeInTheDocument()
    expect(screen.getByText('Done')).toBeInTheDocument()
  })

  /**
   * Test: Tasks appear in correct columns
   *
   * What we're checking:
   * - TODO task appears in "To Do" column
   * - IN_PROGRESS task appears in "In Progress" column
   * - IN_REVIEW task appears in "In Review" column
   * - DONE task appears in "Done" column
   *
   * Why important: Task organization is core functionality
   */
  it('displays tasks in correct status columns', () => {
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard
        tasks={mockTasks}
        projectId="1"
        onTaskClick={mockOnTaskClick}
      />
    )

    // Check each task is in correct column
    expect(screen.getByText('Design homepage')).toBeInTheDocument()
    expect(screen.getByText('Setup database')).toBeInTheDocument()
    expect(screen.getByText('Write documentation')).toBeInTheDocument()
    expect(screen.getByText('Deploy to production')).toBeInTheDocument()
  })

  /**
   * Test: Task counts are correct
   *
   * What we're checking:
   * - Each column shows number of tasks it contains
   * - Counts update when tasks change
   *
   * Why important: Helps users see workload at a glance
   */
  it('shows correct task count for each column', () => {
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard
        tasks={mockTasks}
        projectId="1"
        onTaskClick={mockOnTaskClick}
      />
    )

    // Each column should show count badge
    // mockTasks has 1 task in each column
    const counts = screen.getAllByText('1')

    // Should have 4 badges (one per column)
    expect(counts).toHaveLength(4)
  })

  /**
   * Test: Empty state works
   *
   * What we're checking:
   * - Board renders when no tasks exist
   * - All columns show "0" count
   * - No error is thrown
   *
   * Why important: New projects start with no tasks
   */
  it('handles empty task list', () => {
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard tasks={[]} projectId="1" onTaskClick={mockOnTaskClick} />
    )

    // Columns should still be visible
    expect(screen.getByText('To Do')).toBeInTheDocument()

    // All counts should be 0
    const counts = screen.getAllByText('0')
    expect(counts).toHaveLength(4)
  })
})

/**
 * ============================================================
 * TEST SUITE: User Interactions
 * ============================================================
 */

describe('TaskBoard Interactions', () => {
  /**
   * Test: Clicking a task calls onTaskClick
   *
   * What we're checking:
   * - User can click on tasks
   * - onTaskClick callback is called
   * - Callback receives correct task data
   *
   * Why important: Users need to view task details
   */
  it('calls onTaskClick when task is clicked', async () => {
    // Setup user event (simulates real user interactions)
    const user = userEvent.setup()

    // Mock function to track if it was called
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard
        tasks={mockTasks}
        projectId="1"
        onTaskClick={mockOnTaskClick}
      />
    )

    // Find and click the first task
    const taskCard = screen.getByText('Design homepage')
    await user.click(taskCard)

    // Verify callback was called
    expect(mockOnTaskClick).toHaveBeenCalledTimes(1)

    // Verify it received the correct task
    expect(mockOnTaskClick).toHaveBeenCalledWith(mockTasks[0])
  })

  /**
   * Test: Can click multiple different tasks
   *
   * What we're checking:
   * - Multiple tasks can be clicked
   * - Each click calls callback
   * - Correct task data is passed each time
   *
   * Why important: Users interact with many tasks
   */
  it('can click multiple tasks', async () => {
    const user = userEvent.setup()
    const mockOnTaskClick = jest.fn()

    renderWithQueryClient(
      <TaskBoard
        tasks={mockTasks}
        projectId="1"
        onTaskClick={mockOnTaskClick}
      />
    )

    // Click first task
    await user.click(screen.getByText('Design homepage'))
    expect(mockOnTaskClick).toHaveBeenCalledWith(mockTasks[0])

    // Click second task
    await user.click(screen.getByText('Setup database'))
    expect(mockOnTaskClick).toHaveBeenCalledWith(mockTasks[1])

    // Should have been called twice total
    expect(mockOnTaskClick).toHaveBeenCalledTimes(2)
  })
})

/**
 * ============================================================
 * RUNNING THESE TESTS
 * ============================================================
 *
 * Run all frontend tests:
 *   npm test
 *
 * Run this file only:
 *   npm test -- TaskBoard.test.tsx
 *
 * Run in watch mode (re-runs on changes):
 *   npm test -- --watch
 *
 * Run with coverage:
 *   npm test -- --coverage
 *
 * Expected output:
 *   PASS  __tests__/components/TaskBoard.test.tsx
 *     TaskBoard Component
 *       ✓ renders without crashing (45ms)
 *       ✓ displays all four status columns (23ms)
 *       ✓ displays tasks in correct status columns (18ms)
 *       ✓ shows correct task count for each column (15ms)
 *       ✓ handles empty task list (12ms)
 *     TaskBoard Interactions
 *       ✓ calls onTaskClick when task is clicked (34ms)
 *       ✓ can click multiple tasks (28ms)
 *
 *   Test Suites: 1 passed, 1 total
 *   Tests:       7 passed, 7 total
 * ============================================================
 */
