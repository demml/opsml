import type { ThemeRegistration } from "shiki";

export const customTheme: ThemeRegistration = {
  name: "custom-light",
  type: "light",
  colors: {
    "editor.background": "#ffffffff",
    "editor.foreground": "#2e3440",
  },
  tokenColors: [
    {
      scope: [
        "keyword",
        "keyword.control",
        "keyword.operator",
        "variable.language",
        "entity.other.attribute-name",
        "support.type.property-name",
      ],
      settings: {
        foreground: "#4b3978",
        fontStyle: "bold",
      },
    },
    {
      scope: [
        "string",
        "string.quoted",
        "constant.numeric",
        "constant.language",
        "constant.character",
        "entity.name.tag",
        "entity.name.type",
        "support.constant",
      ],
      settings: {
        foreground: "#04a27a",
      },
    },
    {
      scope: ["comment", "comment.line", "comment.block"],
      settings: {
        foreground: "#888888",
        fontStyle: "italic",
      },
    },
    {
      scope: ["entity.name.function", "support.function", "meta.function-call"],
      settings: {
        foreground: "#4b3978",
      },
    },
    {
      scope: [
        "punctuation",
        "punctuation.definition",
        "punctuation.separator",
        "punctuation.terminator",
      ],
      settings: {
        foreground: "#2e3440",
      },
    },
  ],
};

export const tracebackTheme: ThemeRegistration = {
  name: "traceback-theme",
  type: "light",
  colors: {
    "editor.background": "#fef2f2", // Light red background
    "editor.foreground": "#7f1d1d", // Dark red text
  },
  tokenColors: [
    // File paths - bright purple/primary for maximum visibility
    {
      scope: [
        "string.quoted.double",
        "string.quoted.single",
        "markup.underline.link",
        "entity.name.tag",
      ],
      settings: {
        foreground: "#6b21a8", // Deep purple
        fontStyle: "bold",
      },
    },
    // Line numbers, function names, and numeric values - bright teal
    {
      scope: [
        "constant.numeric",
        "constant.language",
        "entity.name.function",
        "support.function",
      ],
      settings: {
        foreground: "#04a27a", // Bright teal/cyan
        fontStyle: "bold",
      },
    },
    // Error types and exception names - bright red
    {
      scope: [
        "entity.name.type",
        "entity.name.class",
        "support.class",
        "entity.name.exception",
        "keyword.control.exception",
      ],
      settings: {
        foreground: "#dc2626", // Bright red
        fontStyle: "bold",
      },
    },
    // Error messages - dark red for readability
    {
      scope: [
        "string",
        "meta.structure.dictionary.value.json string.quoted.double.json",
      ],
      settings: {
        foreground: "#991b1b", // Dark red
        fontStyle: "normal",
      },
    },
    // Keywords like "File", "in", "line", "raise" - bright violet
    {
      scope: ["keyword", "keyword.control", "keyword.operator", "storage.type"],
      settings: {
        foreground: "#7c3aed", // Bright violet
        fontStyle: "bold",
      },
    },
    // Variable names and identifiers - orange for contrast
    {
      scope: [
        "variable",
        "variable.parameter",
        "variable.other",
        "meta.definition.variable",
      ],
      settings: {
        foreground: "#ea580c", // Bright orange
        fontStyle: "normal",
      },
    },
    // Caret markers (^^^^^) - bright red with underline
    {
      scope: ["markup.error", "invalid", "invalid.illegal"],
      settings: {
        foreground: "#dc2626",
        fontStyle: "bold underline",
      },
    },
    // Punctuation and operators - medium gray for subtle contrast
    {
      scope: ["punctuation", "punctuation.definition"],
      settings: {
        foreground: "#64748b", // Slate gray
      },
    },
    // Comments - muted gray italic
    {
      scope: ["comment", "comment.line", "comment.block"],
      settings: {
        foreground: "#94a3b8", // Light slate
        fontStyle: "italic",
      },
    },
  ],
};
