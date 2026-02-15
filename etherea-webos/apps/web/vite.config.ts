import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { visualizer } from 'rollup-plugin-visualizer';

const analyze = process.env.ANALYZE === '1';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
        cleanupOutdatedCaches: true,
        globIgnores: [
          '**/*.map',
          '**/assets/*.map',
          '**/assets/vendor_monaco-*.js',
          '**/assets/vendor_pdfjs-*.js',
        ],
        runtimeCaching: [
          {
            urlPattern: /\/assets\/vendor_(monaco|pdfjs)-.*\.js$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'etherea-large-vendors',
              expiration: {
                maxEntries: 6,
                maxAgeSeconds: 60 * 60 * 24 * 7,
              },
            },
          },
        ],
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
    ...(analyze
      ? [
          visualizer({
            filename: 'dist/bundle-report.html',
            template: 'treemap',
            gzipSize: true,
            brotliSize: true,
          }),
        ]
      : []),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;
          if (id.includes('react')) return 'vendor_react';
          if (id.includes('@etherea/ui')) return 'vendor_ui';
          if (id.includes('monaco-editor')) return 'vendor_monaco';
          if (id.includes('pdfjs-dist')) return 'vendor_pdfjs';
          if (id.includes('three')) return 'vendor_three';
          return 'vendor';
        },
      },
    },
  },
});
