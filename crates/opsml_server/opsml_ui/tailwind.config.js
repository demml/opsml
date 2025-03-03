// @ts-check
import { join } from "path";

import { skeleton } from "@skeletonlabs/tw-plugin";
import { opsmlTheme } from "./opsml-theme";
import forms from "@tailwindcss/forms";

/** @type {import('tailwindcss').Config} */

const config = {
  content: [
    "./src/**/*.{html,js,svelte,ts}",
    join(
      require.resolve("@skeletonlabs/skeleton"),
      "../**/*.{html,js,svelte,ts}"
    ),
  ],

  darkMode: "class",

  theme: {
    extend: {
      colors: {
        darkpurple: "#4b3978",
        scouter_red: "#f54d55",
      },
    },
  },
  plugins: [
    forms,
    skeleton({
      themes: { custom: [opsmlTheme] },
    }),
  ],
};

module.exports = config;
