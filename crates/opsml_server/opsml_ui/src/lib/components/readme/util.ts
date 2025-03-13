import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type { CardQueryArgs, ReadMeArgs } from "../api/schema";
import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import "github-markdown-css/github-markdown-light.css";

export type ReadMe = {
  readme: string;
  exists: boolean;
};

export async function getCardReadMe(
  name: string,
  repository: string,
  version: string,
  registry_type: RegistryType
): Promise<ReadMe> {
  const params: CardQueryArgs = {
    name: name,
    repository: repository,
    version: version,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(RoutePaths.README, params);
  return await response.json();
}

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

/**
 * Update the readme for a card
 * @param readme The new readme
 */
export async function putReadMe(
  name: string,
  repository: string,
  registry_type: RegistryType,
  content: string
) {
  let args: ReadMeArgs = {
    name: name,
    repository: repository,
    registry_type: registry_type,
    content: content,
  };

  await opsmlClient.put(RoutePaths.README, args);
}
