import tailwindcss from "@tailwindcss/vite";
import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit(), tailwindcss(), svelteTesting()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest-setup.ts"],
  },
});
