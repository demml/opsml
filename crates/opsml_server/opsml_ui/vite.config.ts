import tailwindcss from "@tailwindcss/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit(), tailwindcss()],
});
