import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type { CardQueryArgs, ReadMeArgs } from "../api/schema";
import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import "github-markdown-css/github-markdown-light.css";
import { userStore } from "../user/user.svelte";

export type ReadMe = {
  readme: string;
  exists: boolean;
};

export async function getCardReadMe(
  name: string,
  space: string,
  registry_type: RegistryType
): Promise<ReadMe> {
  const params: CardQueryArgs = {
    name: name,
    space: space,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(
    RoutePaths.README,
    params,
    userStore.jwt_token
  );
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

export type UploadResponse = {
  uploaded: boolean;
  message: string;
};

export async function createReadMe(
  name: string,
  space: string,
  registry_type: RegistryType,
  content: string
): Promise<UploadResponse> {
  let args: ReadMeArgs = {
    space: space,
    name: name,
    registry_type: registry_type,
    readme: content,
  };

  return (
    await opsmlClient.post(RoutePaths.README, args, userStore.jwt_token)
  ).json();
}
