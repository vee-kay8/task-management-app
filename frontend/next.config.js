/** @type {import('next').NextConfig} */
const nextConfig = {
  // ============================================================
  // REACT STRICT MODE
  // ============================================================
  // Enables additional checks and warnings in development
  // Helps identify potential problems in the application
  reactStrictMode: true,
  
  // ============================================================
  // OUTPUT MODE - CRITICAL FOR DOCKER
  // ============================================================
  // 'standalone' mode creates a minimal production server
  // This dramatically reduces Docker image size
  // 
  // HOW IT WORKS:
  // - Next.js traces which files are needed for production
  // - Creates .next/standalone folder with minimal dependencies
  // - Only includes required node_modules (not all of them)
  // - Results in 80-90% smaller Docker images
  //
  // WITHOUT STANDALONE: ~1.2 GB Docker image
  // WITH STANDALONE: ~150-200 MB Docker image
  output: 'standalone',
  
  // ============================================================
  // ENVIRONMENT VARIABLES
  // ============================================================
  // NEXT_PUBLIC_* variables are embedded at build time
  // They become available in the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api',
  },
  
  // ============================================================
  // IMAGE OPTIMIZATION
  // ============================================================
  // Configure how Next.js optimizes images
  images: {
    // Domains allowed for image optimization
    // Add your image CDN domains here if needed
    domains: [],
    
    // Disable image optimization in Docker if needed
    // Uncomment if you face issues with sharp in Alpine Linux
    // unoptimized: true,
  },
  
  // ============================================================
  // COMPRESSION
  // ============================================================
  // Enable gzip compression for responses
  // Reduces bandwidth usage
  compress: true,
  
  // ============================================================
  // PRODUCTION OPTIMIZATIONS
  // ============================================================
  // These settings are applied automatically in production
  // but explicitly defining them makes behavior predictable
  
  // Enable SWC minification (faster than Terser)
  swcMinify: true,
  
  // ============================================================
  // CUSTOM WEBPACK CONFIGURATION (if needed)
  // ============================================================
  // Uncomment and modify if you need custom webpack config
  // webpack: (config, { isServer }) => {
  //   // Custom webpack configuration
  //   return config
  // },
}

module.exports = nextConfig
