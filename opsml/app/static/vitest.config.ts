/// <reference types="vitest" />
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import path from "path";

export default defineConfig({
  plugins: [svelte()],
  test: {
    include: ["./src/tests/*.test.ts"],
    environment: "jsdom",
    coverage: {
      include: ["**/src/**"],
      exclude: ["**/src/lib/Navbar.svelte"],
    },
    globals: true,
  },
  resolve: {
    alias: {
      $lib: path.resolve(__dirname, "./src/lib"),
      $app: path.resolve(__dirname, "__mocks__/app"),
      $routes: path.resolve(__dirname, "./src/routes"),
    },
  },
});
