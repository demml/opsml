import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { generateText } from "ai";
import { opsmlClient } from "$lib/components/api/client.svelte";
import { type Message } from "$lib/components/card/prompt/types";
import { RoutePaths } from "$lib/components/api/routes";
import { createVertex } from "@ai-sdk/google-vertex";

export interface ProviderKeyRequest {
  provider: ProviderType;
}

export interface spaceResponse {
  spaces: string[];
}

export enum ProviderType {
  OpenAI = "openai",
  Anthropic = "anthropic",
}

async function getProviderKey(provider: ProviderType): Promise<string> {
  let request: ProviderKeyRequest = {
    provider: provider,
  };

  const response = await opsmlClient.get(RoutePaths.PROVIDER_KEY, request);
  return await response.json();
}

function getProvider(provider: ProviderType, apiKey: string) {
  switch (provider) {
    case ProviderType.OpenAI:
      return createOpenAI({ apiKey });
    case ProviderType.Anthropic:
      return createAnthropic({ apiKey });
    default:
      throw new Error(`Unsupported provider: ${provider}`);
  }
}

/**
 * Generates text from an llm provider
 * @param apiKey - The API key for the provider
 * @param model - The model to use for generation
 * @param messages - The messages to send to the model
 * @param provider - The provider to use for generation
 * @param extraParams - Extra parameters to pass to the model
 */
export async function generateOpenAiText(
  apiKey: string | undefined,
  model: string,
  messages: Message[],
  provider: ProviderType,
  extraParams: any = {}
) {
  // Check if apiKey is provided, if not, fetch it from the server
  if (!apiKey) {
    apiKey = await getProviderKey(provider);
  }

  // setup provider
  const text_provider = getProvider(provider, apiKey);

  let prompt_messages = messages.map((message) => {
    return {
      role: message.role,
      content: message.content,
    };
  });

  generateText({
    model: text_provider(model),
    messages: prompt_messages,
    ...extraParams,
  });
}
