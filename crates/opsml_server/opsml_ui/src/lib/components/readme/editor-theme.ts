import { EditorView } from "@codemirror/view";

const base = "#2e3440";
const background = "#ffffff";

/// The editor theme styles for Basic Light.
export const editorTheme = EditorView.theme({
  "&": {
    color: base,
    backgroundColor: background,
    border: "none",
    fontSize: "14pt",
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
