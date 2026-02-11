import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',

      // ✅ Fix for your CI error: allow larger files to be precached
      // Default is 2 MiB; your bundle is ~4.33 MiB
      workbox: {
        maximumFileSizeToCacheInBytes: 6 * 1024 * 1024, // 6 MiB
      },

      manifest: {
        name: 'Etherea Adaptive OS',
        short_name: 'Etherea',
        theme_color: '#090b1a',
        background_color: '#090b1a',
        display: 'standalone',
        start_url: '/',
        icons: [],
      },
    }),
  ],

  // ✅ Optional but recommended: reduce mega-bundle size (helps PWA + load time)
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) return 'vendor';
        },
      },
    },
  },
});
