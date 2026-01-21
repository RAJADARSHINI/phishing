import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analyze': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analyze_email': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/predict-email': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/predict-url': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    }
  }
})
