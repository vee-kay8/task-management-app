# ============================================================
# MULTI-STAGE DOCKERFILE FOR NEXT.JS FRONTEND
# ============================================================
# This Dockerfile creates an optimized production build for our
# Next.js application using a multi-stage approach.
#
# NEXT.JS DEPLOYMENT MODES:
# Next.js 14 offers different output modes:
# 1. Standalone - Minimal production server (our choice)
# 2. Static Export - Pre-rendered static HTML
# 3. Server - Full Next.js server
#
# We use "standalone" mode which:
# - Creates a minimal Node.js server
# - Only includes necessary dependencies
# - Results in smallest possible Docker image
# - Supports all Next.js features (SSR, API routes, etc.)
#
# STAGES:
# 1. Dependencies - Install all node_modules
# 2. Builder - Build the Next.js application
# 3. Runner - Production runtime with minimal footprint
# ============================================================

# ============================================================
# STAGE 1: DEPENDENCIES
# ============================================================
# Purpose: Install all Node.js dependencies
# This stage caches node_modules for faster subsequent builds

FROM node:18-alpine AS deps

# ============================================================
# IMAGE METADATA (OCI Labels)
# ============================================================
# Following Open Container Initiative (OCI) annotation standards
# https://github.com/opencontainers/image-spec/blob/main/annotations.md

LABEL org.opencontainers.image.title="Task Management Frontend"
LABEL org.opencontainers.image.description="Next.js Frontend Application for Task Management"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="vee-kay8"
LABEL org.opencontainers.image.vendor="Task Management Project"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/vee-kay8/task-management-app"
LABEL org.opencontainers.image.documentation="https://github.com/vee-kay8/task-management-app/blob/main/README.md"

# Custom labels for internal metadata
LABEL app.name="task-management-frontend"
LABEL app.component="ui"
LABEL app.tier="frontend"
LABEL app.runtime="node"
LABEL app.runtime.version="18"
LABEL app.framework="nextjs"
LABEL app.framework.version="14.2.35"
LABEL maintainer="vee-kay8"
LABEL stage="deps"

# WHY node:18-alpine?
# - node:18: Matches our development Node.js version
# - alpine: Minimal Linux distribution (~5MB vs ~100MB for standard)
# - alpine uses musl libc instead of glibc (smaller but compatible)

# ============================================================
# INSTALL SYSTEM DEPENDENCIES
# ============================================================
# Some npm packages need native compilation
# Alpine needs these packages for building native modules

RUN apk add --no-cache \
    # libc6-compat: Compatibility layer for packages expecting glibc
    libc6-compat \
    # python3: Some npm packages need Python for build scripts
    python3 \
    # make: Build tool required by some packages
    make \
    # g++: C++ compiler for native modules
    g++

# WHY apk ADD --no-cache?
# - apk is Alpine's package manager (like apt on Ubuntu)
# - --no-cache: Don't store package index locally (saves space)

# ============================================================
# SET WORKING DIRECTORY
# ============================================================

WORKDIR /app

# All subsequent commands run from /app directory
# This is where our application will live

# ============================================================
# COPY DEPENDENCY FILES
# ============================================================
# Copy only package files first (not all code)
# This leverages Docker layer caching

COPY package.json package-lock.json* ./

# WHY COPY package.json SEPARATELY?
# Docker caches each layer. If package.json hasn't changed,
# Docker reuses the cached node_modules layer.
# This makes rebuilds much faster when only code changes.

# package-lock.json*: The * makes it optional
# Some projects don't use lock files, this prevents build failure

# ============================================================
# INSTALL DEPENDENCIES
# ============================================================

# Install all dependencies (including devDependencies)
# We need devDependencies for the build process
RUN npm ci

# WHY npm ci INSTEAD OF npm install?
# npm ci (clean install):
# - Faster than npm install (10-20x in CI environments)
# - Uses package-lock.json for exact versions
# - Removes existing node_modules first (clean slate)
# - Fails if package.json and package-lock.json are out of sync
# - More reliable for production builds

# Alternative if no package-lock.json:
# RUN npm install --frozen-lockfile

# ============================================================
# STAGE 2: BUILDER
# ============================================================
# Purpose: Build the Next.js application for production

FROM node:18-alpine AS builder

LABEL maintainer="vee-kay8"
LABEL description="Task Management Frontend - Builder Stage"
LABEL stage="builder"

WORKDIR /app

# ============================================================
# COPY DEPENDENCIES FROM PREVIOUS STAGE
# ============================================================
# Instead of reinstalling, copy from deps stage
# This reuses the cached layer and speeds up builds

COPY --from=deps /app/node_modules ./node_modules

# ============================================================
# COPY APPLICATION CODE
# ============================================================
# Now copy all the source code

COPY . .

# This includes:
# - app/ directory (Next.js app router)
# - components/ directory (React components)
# - lib/ directory (utilities and API client)
# - public/ directory (static assets)
# - Configuration files (next.config.js, tsconfig.json, etc.)

# ============================================================
# BUILD-TIME ENVIRONMENT VARIABLES
# ============================================================
# Next.js differentiates between build-time and runtime variables

# NEXT_TELEMETRY_DISABLED: Disable Next.js anonymous telemetry
# This prevents Next.js from sending usage data to Vercel
ENV NEXT_TELEMETRY_DISABLED 1

# NODE_ENV: Tell Node.js this is a production build
# This enables optimizations in Next.js and other packages
ENV NODE_ENV production

# WHY SET THESE AT BUILD TIME?
# - Some optimizations only apply during build
# - Tree-shaking removes development-only code
# - Minification and compression are more aggressive

# ============================================================
# BUILD THE APPLICATION
# ============================================================

# Run Next.js production build
RUN npm run build

# WHAT HAPPENS DURING BUILD?
# 1. TypeScript compilation (if using TypeScript)
# 2. Code bundling and optimization
# 3. Static page generation (if applicable)
# 4. CSS processing and minification
# 5. Image optimization preparation
# 6. Creation of .next/standalone folder (our target)

# OUTPUT STRUCTURE:
# .next/
#   ├── cache/           (build cache, not needed in production)
#   ├── server/          (server-side code)
#   ├── static/          (static assets with hashes)
#   └── standalone/      (minimal production server - we'll use this)

# THE STANDALONE FOLDER:
# - Contains only code needed to run the app
# - Includes minimal node_modules
# - Much smaller than full node_modules
# - Self-contained Node.js server

# ============================================================
# STAGE 3: RUNNER (PRODUCTION)
# ============================================================
# Purpose: Create minimal production image with only runtime needs

FROM node:18-alpine AS runner

LABEL maintainer="vee-kay8"
LABEL description="Task Management Frontend - Production Runtime"
LABEL version="1.0.0"
LABEL stage="runner"

WORKDIR /app

# ============================================================
# SET PRODUCTION ENVIRONMENT
# ============================================================

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# ============================================================
# CREATE NON-ROOT USER
# ============================================================
# SECURITY BEST PRACTICE: Never run containers as root

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# WHAT THIS DOES:
# addgroup --system --gid 1001 nodejs:
#   - Creates a system group named 'nodejs'
#   - Assigns group ID 1001
#   - --system: Marks it as a system group
#
# adduser --system --uid 1001 nextjs:
#   - Creates a system user named 'nextjs'
#   - Assigns user ID 1001
#   - --system: No password, no home directory shell

# WHY SPECIFIC IDs (1001)?
# - Consistency across containers
# - Makes file permissions predictable
# - Easier debugging and security audits

# ============================================================
# COPY PUBLIC ASSETS
# ============================================================
# Public directory contains static files (images, fonts, etc.)
# These are served directly without processing

COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# ============================================================
# COPY STANDALONE OUTPUT
# ============================================================
# This is the magic of Next.js standalone mode
# It contains everything needed to run the app

# Set proper permissions with --chown
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# WHAT WE'RE COPYING:
# 1. .next/standalone/ - Minimal Next.js server + required node_modules
# 2. .next/static/ - Static assets (JS, CSS bundles with hashes)

# WHY SEPARATE STATIC FOLDER?
# - Standalone mode doesn't include .next/static automatically
# - Static files are served at /_next/static/
# - Essential for CSS, JS, and optimized images

# ============================================================
# SET OWNERSHIP
# ============================================================
# Ensure nextjs user owns all application files

RUN chown -R nextjs:nodejs /app

# -R: Recursive (all subdirectories)
# This ensures the nextjs user can read all files

# ============================================================
# SWITCH TO NON-ROOT USER
# ============================================================

USER nextjs

# All subsequent commands (including CMD) run as nextjs user
# If the container is compromised, attacker has limited permissions

# ============================================================
# EXPOSE PORT
# ============================================================

EXPOSE 3000

# Next.js standalone server runs on port 3000 by default
# This is documentation only - actual port mapping in docker-compose

# ============================================================
# ENVIRONMENT VARIABLE CONFIGURATION
# ============================================================
# These can be overridden at runtime via docker-compose or docker run

# Port the application listens on
ENV PORT 3000

# Hostname - 0.0.0.0 allows external connections
# localhost would only allow connections from inside the container
ENV HOSTNAME "0.0.0.0"

# API URL - Points to backend service
# Will be overridden in docker-compose to use service name
ENV NEXT_PUBLIC_API_URL http://localhost:5000/api

# ============================================================
# HEALTH CHECK
# ============================================================
# Tells Docker how to check if the container is healthy

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# PARAMETERS EXPLAINED:
# --interval=30s: Check every 30 seconds
# --timeout=10s: Fail if check takes > 10 seconds
# --start-period=30s: Wait 30 seconds before first check (app startup time)
# --retries=3: Mark unhealthy after 3 consecutive failures

# HEALTH CHECK COMMAND:
# Uses Node.js built-in http module to make a GET request
# Checks if /api/health returns 200 status code
# process.exit(0): Success
# process.exit(1): Failure

# NOTE: We'll need to create the /api/health endpoint
# This will be a simple API route in Next.js

# ============================================================
# STARTUP COMMAND
# ============================================================

CMD ["node", "server.js"]

# WHAT IS server.js?
# Next.js standalone mode creates a server.js file
# This is a minimal Node.js server that serves your app
# Much lighter than running `next start`

# WHY NOT "next start"?
# - next start includes full Next.js CLI
# - server.js is a lightweight production server
# - Smaller memory footprint
# - Faster startup time

# ============================================================
# BUILD AND RUN INSTRUCTIONS
# ============================================================
#
# BUILD THE IMAGE:
# docker build -t task-management-frontend:latest ./frontend
#
# RUN THE CONTAINER (standalone):
# docker run -d \
#   -p 3000:3000 \
#   -e NEXT_PUBLIC_API_URL=http://localhost:5000/api \
#   --name frontend \
#   task-management-frontend:latest
#
# VIEW LOGS:
# docker logs -f frontend
#
# STOP AND REMOVE:
# docker stop frontend && docker rm frontend
#
# ============================================================
# IMAGE SIZE COMPARISON
# ============================================================
# Without multi-stage build: ~1.2 GB
# With multi-stage + standalone: ~150-200 MB
# Savings: ~85% reduction in image size
# ============================================================
#
# TROUBLESHOOTING
# ============================================================
#
# Issue: "Error: Could not find a production build"
# Solution: Ensure next.config.js has output: 'standalone'
#
# Issue: Static assets not loading
# Solution: Verify .next/static is copied to the runner stage
#
# Issue: API calls failing
# Solution: Check NEXT_PUBLIC_API_URL environment variable
#
# ============================================================
