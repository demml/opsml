import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";
import { preprocessMeltUI, sequence } from "@melt-ui/pp";

export default {
  kit: {
    prerender: {
      handleHttpError: "ignore",
    },
    appDir: "app",
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
    alias: {
      $routes: "./src/routes",
      "$routes/*": "./src/routes/*",
    },
  },
  compilerOptions: {
    runes: true,
  },
  preprocess: sequence([vitePreprocess(), preprocessMeltUI()]),
  vitePlugin: { exclude: ["./node_modules", "./.svelte-kit", "./.svelte"] },
};
