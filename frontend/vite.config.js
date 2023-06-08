import relay from "vite-plugin-relay";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [relay, react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/setupTests.jsx",
    // you might want to disable it, if you don't have tests that rely on CSS
    // since parsing CSS is slow
    threads: false,
    css: false,
    coverage: {
      provider: "istanbul",
      reporter: ["html", "cobertura"],
      reportsDirectory: "./reports",
    },
  },
});
