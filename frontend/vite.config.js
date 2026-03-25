/**
 * @module ViteConfig
 * @desc Konfigurasi Vite build tool untuk proyek React Zonara.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
