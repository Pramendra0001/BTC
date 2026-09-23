import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  plugins: [react(), tailwindcss()],
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
              return 'vendor-react'
            }
            if (id.includes('@tanstack/react-query') || id.includes('axios')) {
              return 'vendor-query'
            }
            if (id.includes('recharts')) {
              return 'vendor-charts'
            }
            if (id.includes('cytoscape') || id.includes('react-cytoscapejs')) {
              return 'vendor-graph'
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons'
            }
            return 'vendor-misc'
          }
        }
      }
    }
  }
})
