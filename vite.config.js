import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5000,
    host: true  // Listen on 0.0.0.0 so it’s accessible outside the container
  }
});