import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        // Use 127.0.0.1 (IPv4) not "localhost": on Node 18+ "localhost" can
        // resolve to IPv6 ::1, but uvicorn listens on IPv4 -> ECONNREFUSED ::1.
        target: process.env.VITE_API_TARGET || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
