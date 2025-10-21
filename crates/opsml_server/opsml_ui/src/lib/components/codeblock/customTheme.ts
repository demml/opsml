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
