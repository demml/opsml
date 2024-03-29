import { EditorView } from "@codemirror/view";

const editorTheme = EditorView.theme({
  "&": {
    fontSize: "11pt",
    border: "none",
  },

  "&.cm-editor.cm-focused": {
    outline: "none",
  },

  ".cm-content": {
    backgroundColor: "#fcfcfc",
  },
  "&.cm-focused .cm-cursor": {
    borderLeftColor: "#4b3978",
  },

  ".cm-gutters": {
    backgroundColor: "#fcfcfc",
    border: "none",
  },

  ".cm-activeLine": {
    backgroundColor: "#e4e1eb",
  },

  ".cm-activeLineGutter": {
    backgroundColor: "#e4e1eb",
  },
});

export default editorTheme;
