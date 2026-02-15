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
          '**/assets/vendor-*.js',
          '**/assets/vendor_*.js',
          '**/assets/chunk-large-*.js',
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
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/react')) return 'vendor-react';
          if (id.includes('node_modules/vite-plugin-pwa')) return 'vendor-pwa';
          if (id.includes('node_modules')) return 'vendor-core';
          return undefined;
        },
      },
    },
  },
});
