/**
 * ============================================================
 * HEALTH CHECK API ROUTE
 * ============================================================
 * 
 * This API route is used by Docker's HEALTHCHECK instruction
 * to verify that the Next.js container is running properly.
 * 
 * PURPOSE:
 * - Container health monitoring
 * - Load balancer health checks
 * - Orchestration systems (Kubernetes, Docker Swarm)
 * - Monitoring tools (Prometheus, etc.)
 * 
 * ENDPOINT: GET /api/health
 * 
 * RESPONSE:
 * {
 *   "status": "healthy",
 *   "service": "task-management-frontend",
 *   "timestamp": "2026-01-02T10:30:00.000Z",
 *   "uptime": 12345
 * }
 * 
 * USAGE IN DOCKER:
 * HEALTHCHECK CMD node -e "require('http').get('http://localhost:3000/api/health', ...)"
 * 
 * ============================================================
 */

import { NextResponse } from 'next/server';

/**
 * GET handler for health check endpoint
 * 
 * This is a Next.js 14 App Router API route.
 * It runs on the server side only.
 * 
 * @returns {NextResponse} JSON response with health status
 */
export async function GET() {
  // Get current timestamp
  const timestamp = new Date().toISOString();
  
  // Get process uptime in seconds
  // This shows how long the Node.js process has been running
  const uptime = process.uptime();
  
  // Return health status
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'task-management-frontend',
      timestamp: timestamp,
      uptime: Math.floor(uptime), // Round to whole seconds
      message: 'Service is running normally',
    },
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        // Add cache control headers to prevent caching health checks
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    }
  );
}

/**
 * ALTERNATIVE ADVANCED HEALTH CHECK
 * 
 * For production systems, you might want to check:
 * - Database connectivity
 * - External API availability
 * - Memory usage
 * - Disk space
 * 
 * Example:
 * 
 * export async function GET() {
 *   const checks = {
 *     database: await checkDatabase(),
 *     api: await checkBackendAPI(),
 *     memory: checkMemory(),
 *   };
 * 
 *   const allHealthy = Object.values(checks).every(check => check.healthy);
 * 
 *   return NextResponse.json(
 *     { status: allHealthy ? 'healthy' : 'degraded', checks },
 *     { status: allHealthy ? 200 : 503 }
 *   );
 * }
 */
