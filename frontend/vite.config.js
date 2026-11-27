import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Em dev, /api é redirecionado para a API local (evita CORS).
export default defineConfig({
  // GitHub Pages serve em /<repositório>/: o workflow define VITE_BASE. Em dev e no Cloudflare Pages fica '/'.
  base: process.env.VITE_BASE || '/',
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': { target: 'http://localhost:8000', rewrite: (p) => p.replace(/^\/api/, '') } } },
});
