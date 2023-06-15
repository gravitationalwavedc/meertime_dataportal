import { defineConfig } from "cypress";

export default defineConfig({
  projectId: "k5qs39",
  e2e: {
    baseUrl: "http://localhost:5173",
    setupNodeEvents(on, config) {
      config.defaultCommandTimeout = 30000;

      return config;
    },
  },
});
