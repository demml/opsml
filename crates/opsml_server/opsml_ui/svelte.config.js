import { mdsvex } from "mdsvex";
import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: [vitePreprocess(), mdsvex()],

  kit: {
    paths: {
      relative: false,
    },
    adapter: adapter({
      pages: "site",
      assets: "site",
      fallback: "index.html",
      precompress: false,
      strict: true,
    }),
  },

  extensions: [".svelte", ".svx"],
};

export default config;
