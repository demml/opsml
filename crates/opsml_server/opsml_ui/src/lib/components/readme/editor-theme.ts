import { EditorView } from "@codemirror/view";

const base = "#2e3440";
const background = "#ffffff";

/// The editor theme styles for Basic Light.
export const editorTheme = EditorView.theme({
  "&": {
    color: base,
    backgroundColor: background,
    border: "none",
    fontSize: "10pt",
  },

  "&.cm-editor.cm-focused": {
    outline: "none",
  },

  "&.cm-focused .cm-cursor": {
    borderLeftColor: "#4b3978",
  },

  ".cm-gutters": {
    backgroundColor: background,
    border: "none",
  },

  ".cm-activeLine": {
    backgroundColor: "transparent",
  },

  ".cm-activeLineGutter": {
    backgroundColor: "transparent",
  },

  ".cm-selectionMatch": {
    backgroundColor: "transparent",
  },
});

/// The editor theme styles for Phosphor Green Dark.
export const editorDarkTheme = EditorView.theme({
  "&": {
    color: "#8ddb9f",
    backgroundColor: "#0a120e",
    border: "none",
    fontSize: "10pt",
  },

  "&.cm-editor.cm-focused": {
    outline: "none",
  },

  "&.cm-focused .cm-cursor": {
    borderLeftColor: "#44cc80",
  },

  ".cm-gutters": {
    backgroundColor: "#0a120e",
    border: "none",
    color: "#4a6a55",
  },

  ".cm-activeLine": {
    backgroundColor: "rgba(68, 204, 128, 0.05)",
  },

  ".cm-activeLineGutter": {
    backgroundColor: "transparent",
  },

  ".cm-selectionMatch": {
    backgroundColor: "rgba(68, 204, 128, 0.15)",
  },

  ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": {
    backgroundColor: "rgba(68, 204, 128, 0.2)",
  },
});
