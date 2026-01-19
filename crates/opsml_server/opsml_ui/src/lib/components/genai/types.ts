import type { AnthropicMessageRequestV1 } from "./provider/anthropic/v1/request";
import type {
  ChatMessage,
  OpenAIChatCompletionRequestV1,
} from "./provider/openai/v1/chat/request";
import type { GeminiGenerateContentRequestV1 } from "./provider/google/v1/generate/request";
import type { MessageNum } from "./provider/types";

/**
 * Provider enum for model sources.
 */
export enum Provider {
  OpenAI = "OpenAI",
  Gemini = "Gemini",
  Google = "Google",
  Anthropic = "Anthropic",
  Vertex = "Vertex",
  Undefined = "Undefined",
}

/**
 * ResponseType enum for prompt responses.
 */
export enum ResponseType {
  Score = "Score",
  Pydantic = "Pydantic",
  Null = "Null",
}

export type ProviderRequest =
  | OpenAIChatCompletionRequestV1
  | AnthropicMessageRequestV1
  | GeminiGenerateContentRequestV1;

export type Prompt =
  | {
      provider: Provider.Anthropic;
      request: AnthropicMessageRequestV1;
      model: string;
      version: string;
      parameters: string[];
      response_type: ResponseType;
    }
  | {
      provider: Provider.OpenAI;
      request: OpenAIChatCompletionRequestV1;
      model: string;
      version: string;
      parameters: string[];
      response_type: ResponseType;
    }
  | {
      provider: Provider.Gemini | Provider.Google | Provider.Vertex;
      request: GeminiGenerateContentRequestV1;
      model: string;
      version: string;
      parameters: string[];
      response_type: ResponseType;
    };

/**
 * Type guard to identify OpenAI ChatMessage objects.
 * It checks for the existence of the 'role' property while
 * ensuring it doesn't match the unique structure of Anthropic content blocks.
 */
export const isOpenAIMessage = (m: MessageNum): m is ChatMessage => {
  console.log("Checking OpenAI message:", m);
  return (
    "role" in m &&
    // OpenAI content is either a string or a flat array of parts.
    // Anthropic content parts have a 'type' property (text, image, etc.)
    // but OpenAI also added 'type' in their multi-modal parts, so we
    // often check for the presence of provider-specific keys like 'parts' (Gemini)
    // or 'content' being strictly an array of OpenAI parts.
    !("parts" in m) && // Exclude Gemini
    !(
      "content" in m &&
      Array.isArray(m.content) &&
      m.content.length > 0 &&
      "type" in m.content[0] &&
      m.content[0].type === "text"
    )
    // Note: The specific check depends on how unique your Anthropic/Gemini types are.
  );
};

export function assertNever(value: never): never {
  throw new Error(`Unhandled provider variant: ${JSON.stringify(value)}`);
}

export class PromptHelper {
  /**
   * Dispatches message retrieval based on the Provider tag.
   */
  static getMessages(prompt: Prompt): MessageNum[] {
    switch (prompt.provider) {
      case Provider.Anthropic:
        // request is narrowed to AnthropicMessageRequestV1
        return prompt.request.messages as unknown as MessageNum[];

      case Provider.OpenAI:
        // need to filter out any message with "role": "developer"
        return (prompt.request.messages as unknown as MessageNum[]).filter(
          (m) => (m as ChatMessage).role !== "developer"
        );

      case Provider.Gemini:
      case Provider.Google:
      case Provider.Vertex:
        // request is narrowed to GeminiGenerateContentRequestV1 (contents)
        return prompt.request.contents as unknown as MessageNum[];

      default:
        return assertNever(prompt as never);
    }
  }

  /**
   * Dispatches system instruction retrieval.
   * OpenAI: Filters main messages.
   * Others: Uses dedicated fields.
   */
  static getSystemInstructions(prompt: Prompt): MessageNum[] {
    const request = prompt.request;

    switch (prompt.provider) {
      case Provider.Anthropic:
        return (request as AnthropicMessageRequestV1)
          .system as unknown as MessageNum[];

      case Provider.Gemini:
      case Provider.Google:
      case Provider.Vertex:
        const geminiReq = request as GeminiGenerateContentRequestV1;
        return geminiReq.systemInstruction
          ? [geminiReq.systemInstruction as unknown as MessageNum]
          : [];

      case Provider.OpenAI:
        const openaiReq = request as OpenAIChatCompletionRequestV1;
        return (openaiReq.messages as unknown as MessageNum[]).filter(
          (m) => (m as ChatMessage).role === "developer"
        );

      default:
        return [];
    }
  }

  /**
   * logic: format!("{}:{}", self.provider.as_str(), self.model)
   */
  static getModelIdentifier(prompt: Prompt): string {
    return `${prompt.provider}:${prompt.model}`;
  }
}
