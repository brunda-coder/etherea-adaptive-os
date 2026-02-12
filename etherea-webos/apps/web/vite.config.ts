import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',

      // ✅ Workbox precache size fix:
      // Workbox default is 2 MiB. Your build produced a ~4.33 MiB chunk previously.
      // This prevents CI/build from failing when a chunk is larger.
      workbox: {
        maximumFileSizeToCacheInBytes: 8 * 1024 * 1024, // 8 MiB safety margin
        cleanupOutdatedCaches: true,

        // Don’t precache sourcemaps / dev leftovers
        globIgnores: ['**/*.map', '**/assets/*.map'],
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

  // ✅ Bundle-splitting to reduce "one giant index-*.js"
  // This is the real fix for keeping chunks smaller and faster to load.
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Split all node_modules first
          if (id.includes('node_modules')) {
            // Big known chunks (common bloat culprits)
            if (id.includes('monaco-editor')) return 'vendor_monaco';
            if (id.includes('pdfjs-dist')) return 'vendor_pdfjs';

            // Core libs
            if (id.includes('react')) return 'vendor_react';

            // Everything else
            return 'vendor';
          }
        },
      },
    },
  },
});
