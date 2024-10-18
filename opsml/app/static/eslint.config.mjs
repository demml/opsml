import typescriptEslint from "@typescript-eslint/eslint-plugin";
import _import from "eslint-plugin-import";
import tsdoc from "eslint-plugin-tsdoc";
import unusedImports from "eslint-plugin-unused-imports";
import { fixupPluginRules } from "@eslint/compat";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  {
    ignores: ["**/tests"],
  },
  ...compat.extends(
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ),
  {
    plugins: {
      "@typescript-eslint": typescriptEslint,
      import: fixupPluginRules(_import),
      tsdoc,
      "@typescript-eslint": typescriptEslint,
      "unused-imports": unusedImports,
    },

    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.commonjs,
        vi: true,
      },

      ecmaVersion: "latest",
      sourceType: "script",

      parserOptions: {
        project: ["./tsconfig.json"],
        extraFileExtensions: ["./.svelte-kit"],
      },
    },

    settings: {
      "import/resolver": {
        node: {
          extensions: [".js", ".jsx", ".ts", ".tsx"],
          moduleDirectory: ["node_modules", "src/"],
        },
      },
    },

    rules: {
      "no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",

      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],

      quotes: [
        2,
        "double",
        {
          avoidEscape: true,
        },
      ],

      "import/prefer-default-export": "off",

      "import/no-extraneous-dependencies": [
        "error",
        {
          devDependencies: true,
        },
      ],

      "@typescript-eslint/no-unused-vars": "off",

      "import/extensions": [
        "error",
        "ignorePackages",
        {
          jsx: "never",
          ts: "never",
          tsx: "never",
          "": "never",
        },
      ],
    },
  },
];
