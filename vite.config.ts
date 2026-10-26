import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // Served from https://clius-dev.github.io/kindercoding/, not the domain root.
  base: '/kindercoding/',
  plugins: [react()],
})
