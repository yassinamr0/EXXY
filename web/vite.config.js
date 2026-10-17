import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'

// `npm run build:single` bundles everything (code + 3D models) into one
// index.html, which is how the private preview link is published.
export default defineConfig(({ mode }) => ({
  plugins: [react(), mode === 'single' && viteSingleFile()].filter(Boolean),
  assetsInclude: ['**/*.glb'],
  build: mode === 'single' ? { assetsInlineLimit: Infinity, outDir: 'dist-single' } : {},
}))
