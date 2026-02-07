import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Etherea Adaptive OS",
        short_name: "Etherea",
        start_url: "/",
        display: "standalone",
        background_color: "#0b1024",
        theme_color: "#141f4b",
        icons: []
      }
    })
  ]
});
