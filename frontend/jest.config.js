/**
 * ============================================================
 * JEST CONFIGURATION FOR NEXT.JS
 * ============================================================
 * This file configures Jest to work with Next.js and TypeScript
 * Documentation: https://nextjs.org/docs/testing
 */

// Import Next.js Jest configuration helper
const nextJest = require('next/jest')

/**
 * createJestConfig: Helper from Next.js that configures Jest
 * It automatically handles:
 * - TypeScript compilation
 * - CSS/SCSS imports (converts them to empty objects in tests)
 * - Image imports (mocks them)
 * - Next.js specific features (routing, etc.)
 */
const createJestConfig = nextJest({
  // dir: Path to your Next.js app
  // './' means current directory (where package.json is)
  dir: './',
})

/**
 * Custom Jest Configuration
 * These settings override or extend Next.js defaults
 */
const customJestConfig = {
  // ============================================================
  // TEST ENVIRONMENT
  // ============================================================
  /**
   * setupFilesAfterEnv: Runs before each test file
   * Used to configure testing library, add custom matchers, etc.
   * This file runs AFTER the test framework is installed
   */
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  /**
   * testEnvironment: Simulated environment for tests
   * - 'jsdom': Simulates a browser (has window, document, etc.)
   * - 'node': Node.js environment (no browser APIs)
   *
   * We use 'jsdom' because React components need browser APIs
   */
  testEnvironment: 'jest-environment-jsdom',

  // ============================================================
  // TEST DISCOVERY
  // ============================================================
  /**
   * testMatch: Patterns for finding test files
   * Jest will look for files matching these patterns
   *
   * Pattern 1: Files in __tests__ folder ending in .js, .jsx, .ts, or .tsx
   *   Example: __tests__/components/Button.test.tsx
   *
   * Pattern 2: Any file with .test. or .spec. in name anywhere in the project
   *   Example: Button.test.tsx, api.spec.js
   */
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],

  // ============================================================
  // MODULE PATHS
  // ============================================================
  /**
   * moduleNameMapper: Map import paths to files/mocks
   * Tells Jest how to resolve imports
   *
   * Why needed: Next.js uses special import syntax like:
   *   import Button from '@/components/Button'
   * Jest doesn't understand '@/' by default
   */
  moduleNameMapper: {
    // Map @/* to the current directory
    // '@/components/Button' → '<rootDir>/components/Button'
    '^@/(.*)$': '<rootDir>/$1',
  },

  // ============================================================
  // COVERAGE CONFIGURATION
  // ============================================================
  /**
   * collectCoverageFrom: Which files to include in coverage report
   * Tells Jest which files to measure (not test files themselves)
   */
  collectCoverageFrom: [
    // Include all components
    'components/**/*.{js,jsx,ts,tsx}',

    // Include all pages and app directory files
    'app/**/*.{js,jsx,ts,tsx}',

    // EXCLUDE the following (prefix with !)
    '!**/*.d.ts', // TypeScript definition files
    '!**/node_modules/**', // Third-party packages
    '!**/.next/**', // Next.js build output
    '!**/coverage/**', // Coverage reports
    '!**/jest.config.js', // Config files
  ],

  /**
   * coverageThresholds: Minimum coverage percentages required
   * Tests fail if coverage is below these thresholds
   * Comment out initially, enforce once you have good coverage
   */
  // coverageThresholds: {
  //   global: {
  //     branches: 70,      // 70% of if/else branches covered
  //     functions: 70,     // 70% of functions called in tests
  //     lines: 70,         // 70% of lines executed
  //     statements: 70,    // 70% of statements executed
  //   },
  // },

  /**
   * coveragePathIgnorePatterns: Files to exclude from coverage
   * These files won't count toward coverage percentage
   */
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
    '/coverage/',
    'jest.config.js',
    'jest.setup.js',
  ],

  // ============================================================
  // TEST BEHAVIOR
  // ============================================================
  /**
   * testTimeout: Maximum time (ms) a test can run before failing
   * Default is 5000ms (5 seconds)
   * Increase if you have slow tests (API calls, file uploads, etc.)
   */
  testTimeout: 10000,

  /**
   * verbose: Show detailed test results
   * true = Show each test name as it runs
   * false = Simpler output
   */
  verbose: true,

  /**
   * clearMocks: Automatically clear mock calls between tests
   * Prevents test pollution (one test affecting another)
   * Always set to true
   */
  clearMocks: true,

  /**
   * resetMocks: Reset mock state between tests
   * Ensures each test starts fresh
   */
  resetMocks: true,

  /**
   * restoreMocks: Restore original implementation after each test
   * If you mock Math.random(), it gets restored after test
   */
  restoreMocks: true,

  // ============================================================
  // TRANSFORM
  // ============================================================
  /**
   * transform: How to process different file types
   * Next.js handles this automatically, but you can customize
   *
   * Example customization:
   * transform: {
   *   '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
   * },
   */

  // ============================================================
  // MODULE FILE EXTENSIONS
  // ============================================================
  /**
   * moduleFileExtensions: File extensions Jest should handle
   * Order matters: Jest tries these in order when resolving imports
   */
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
}

/**
 * Export configuration
 * createJestConfig merges our custom config with Next.js defaults
 * This ensures Next.js features work in tests
 */
module.exports = createJestConfig(customJestConfig)

/**
 * ============================================================
 * USAGE EXAMPLES
 * ============================================================
 *
 * Run all tests:
 *   npm test
 *
 * Run tests in watch mode (re-runs on file changes):
 *   npm test -- --watch
 *
 * Run tests with coverage:
 *   npm test -- --coverage
 *
 * Run specific test file:
 *   npm test -- TaskBoard.test.tsx
 *
 * Run tests matching pattern:
 *   npm test -- --testNamePattern="renders"
 *
 * Update snapshots:
 *   npm test -- -u
 *
 * Run tests in debug mode:
 *   node --inspect-brk node_modules/.bin/jest --runInBand
 *
 * ============================================================
 */
