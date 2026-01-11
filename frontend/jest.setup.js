/**
 * ============================================================
 * JEST SETUP FILE
 * ============================================================
 * This file runs once before all tests
 * Used to configure testing library and add custom matchers
 *
 * Runs AFTER Jest is loaded but BEFORE any tests run
 */

/**
 * Import testing-library/jest-dom
 * This adds custom Jest matchers for DOM elements
 * Makes assertions more readable and specific
 *
 * Without jest-dom:
 *   expect(element.textContent).toBe('Hello')
 *
 * With jest-dom:
 *   expect(element).toHaveTextContent('Hello')  ✓ More readable
 */
import '@testing-library/jest-dom'

/**
 * ============================================================
 * CUSTOM MATCHERS PROVIDED BY @testing-library/jest-dom
 * ============================================================
 *
 * These matchers make test assertions more expressive:
 *
 * DOM ELEMENT MATCHERS:
 * - toBeInTheDocument()        // Element exists in DOM
 * - toBeVisible()              // Element is visible (not hidden)
 * - toBeEmpty()                // Element has no children
 * - toContainElement(element)  // Element contains another element
 * - toContainHTML(html)        // Element contains HTML string
 *
 * TEXT CONTENT MATCHERS:
 * - toHaveTextContent(text)    // Element has specific text
 * - toHaveAccessibleName(name) // Element has accessible name
 * - toHaveAccessibleDescription(desc)
 *
 * FORM MATCHERS:
 * - toHaveFormValues(values)   // Form has specific values
 * - toHaveValue(value)         // Input has specific value
 * - toBeChecked()              // Checkbox/radio is checked
 * - toBeEnabled()              // Input is not disabled
 * - toBeDisabled()             // Input is disabled
 * - toBeRequired()             // Input has required attribute
 * - toBeInvalid()              // Input is invalid
 * - toBeValid()                // Input is valid
 *
 * ATTRIBUTE MATCHERS:
 * - toHaveAttribute(attr, value)    // Element has attribute
 * - toHaveClass(className)          // Element has CSS class
 * - toHaveStyle(css)                // Element has inline styles
 *
 * FOCUS MATCHERS:
 * - toHaveFocus()              // Element is currently focused
 *
 * ============================================================
 */

/**
 * ============================================================
 * GLOBAL TEST UTILITIES
 * ============================================================
 * You can add global utilities that all tests can access
 */

/**
 * Mock window.matchMedia
 * Many components check if screen is mobile/desktop
 * jsdom doesn't include matchMedia by default
 *
 * Without this mock, tests fail with:
 *   TypeError: window.matchMedia is not a function
 */
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false, // Desktop by default
    media: query, // Media query string
    onchange: null, // No change listener
    addListener: jest.fn(), // Deprecated but kept for compatibility
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(), // Modern event listener
    removeEventListener: jest.fn(), // Modern event listener
    dispatchEvent: jest.fn(), // Trigger events
  })),
})

/**
 * Mock window.IntersectionObserver
 * Used for lazy loading, infinite scroll, etc.
 * jsdom doesn't include IntersectionObserver
 *
 * Example component that needs this:
 *   const ref = useIntersectionObserver(() => loadMore())
 */
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
}

/**
 * Mock console methods to reduce noise in test output
 * Sometimes you want to suppress expected errors/warnings
 *
 * Uncomment to silence console in tests:
 */
// const originalError = console.error
// beforeAll(() => {
//   console.error = jest.fn()
// })
// afterAll(() => {
//   console.error = originalError
// })

/**
 * ============================================================
 * ENVIRONMENT VARIABLES FOR TESTS
 * ============================================================
 * Set environment variables that tests need
 * These override values in .env file
 */
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:5000/api'

/**
 * ============================================================
 * GLOBAL TEST SETUP/TEARDOWN
 * ============================================================
 * Runs before/after each test file
 */

/**
 * beforeEach: Runs before each test
 * Good for: Resetting state, clearing mocks
 *
 * Uncomment if needed:
 */
// beforeEach(() => {
//   // Clear all mocks before each test
//   jest.clearAllMocks()
// })

/**
 * afterEach: Runs after each test
 * Good for: Cleanup, unmounting components
 *
 * Uncomment if needed:
 */
// import { cleanup } from '@testing-library/react'
// afterEach(() => {
//   cleanup()  // Unmount React components
// })

/**
 * ============================================================
 * CUSTOM TEST UTILITIES
 * ============================================================
 * Add custom helpers that all tests can use
 */

/**
 * Mock user object for tests
 * Prevents repeating this in every test file
 */
global.mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  created_at: '2024-01-01T00:00:00Z',
}

/**
 * Mock project object for tests
 */
global.mockProject = {
  id: 1,
  name: 'Test Project',
  description: 'Test Description',
  owner_id: 1,
  created_at: '2024-01-01T00:00:00Z',
}

/**
 * Mock task object for tests
 */
global.mockTask = {
  id: 1,
  title: 'Test Task',
  description: 'Test Description',
  status: 'todo',
  priority: 'high',
  project_id: 1,
  created_at: '2024-01-01T00:00:00Z',
}

/**
 * ============================================================
 * TESTING BEST PRACTICES
 * ============================================================
 *
 * 1. TEST USER BEHAVIOR, NOT IMPLEMENTATION
 *    ✓ User clicks button, modal appears
 *    ✗ Modal state changes to isOpen: true
 *
 * 2. USE ACCESSIBLE QUERIES
 *    Prefer (in order):
 *    1. getByRole('button', { name: 'Submit' })
 *    2. getByLabelText('Email')
 *    3. getByPlaceholderText('Enter email')
 *    4. getByText('Welcome')
 *    5. getByTestId('submit-button')  // Last resort
 *
 * 3. WAIT FOR ASYNC UPDATES
 *    Use waitFor, findBy queries for async operations:
 *    await waitFor(() => expect(element).toBeInTheDocument())
 *    const element = await screen.findByText('Loaded')
 *
 * 4. MOCK EXTERNAL DEPENDENCIES
 *    Mock API calls, timers, random values:
 *    jest.spyOn(global, 'fetch').mockResolvedValue(...)
 *
 * 5. TEST ERROR STATES
 *    Don't just test happy path, test errors too:
 *    - Network failures
 *    - Invalid input
 *    - Permission denied
 *
 * ============================================================
 */
