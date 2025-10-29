import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: [vitePreprocess()],

  kit: {
    adapter: adapter({
      out: "build",
      precompress: false,
    }),
    csrf: {
      trustedOrigins: [
        "http://0.0.0.0:3000",
        "https://0.0.0.0:3000",
        "http://localhost:3000",
        "https://localhost:3000",
      ],
    },
  },
  extensions: [".svelte"],
};

export default config;
