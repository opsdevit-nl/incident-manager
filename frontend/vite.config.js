import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5000,
    allowedHosts: ['fedora.example.one.com', '10.23.39.255', 'localhosts'],
    host: true  // Listen on 0.0.0.0 so it’s accessible outside the container
  }
});