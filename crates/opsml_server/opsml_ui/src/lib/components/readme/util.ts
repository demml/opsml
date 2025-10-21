import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import "github-markdown-css/github-markdown-light.css";

export type ReadMe = {
  readme: string;
  exists: boolean;
};

export type UploadResponse = {
  uploaded: boolean;
  message: string;
};

// Configure marked with markedHighlight
const marked = new Marked(
  markedHighlight({
    langPrefix: "hljs language-",
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      return hljs.highlight(code, { language }).value;
    },
  })
);

export async function convertMarkdown(markdown: string): Promise<string> {
  // @ts-ignore
  return await marked.parse(markdown);
}
