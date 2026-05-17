import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      reportsDirectory: "coverage",
      thresholds: {
        lines: 70,
        functions: 65,
        branches: 60,
        statements: 70,
      },
      exclude: ["src/main.tsx", "src/**/*.d.ts", "src/test/**"],
    },
  },
});
