import { Provider, ResponseType, Role, type Prompt } from "./types";
import type { OpenAIChatSettings } from "./settings/openai";
import type { GeminiSettings } from "./settings/gemini";

/**
 * Mock OpenAI Prompt
 */
export const mockOpenAIPrompt: Prompt = {
  message: [
    {
      content: { Str: "What is the capital of France?" },
      role: Role.User,
      variables: [],
    },
    {
      content: { Str: "The capital of France is Paris." },
      role: Role.Assistant,
      variables: [],
    },
  ],
  system_instruction: [
    {
      content: { Str: "You are a helpful assistant." },
      role: Role.Assistant || "system",
      variables: [],
    },
  ],
  model_settings: {
    OpenAIChat: {
      max_completion_tokens: 128,
      temperature: 0.7,
      top_p: 1,
      stop_sequences: ["\n"],
      audio: { format: "mp3", voice: "en-US-Wavenet-D" },
      tool_choice: { mode: "auto" },
      tools: [],
      metadata: { project: "demo" },
    } as OpenAIChatSettings,
  },
  model: "gpt-4",
  provider: Provider.OpenAI,
  version: "1.0.0",
  response_json_schema: undefined,
  parameters: ["capital", "country"],
  response_type: ResponseType.Pydantic,
};

/**
 * Mock Gemini Prompt
 */
export const mockGeminiPrompt: Prompt = {
  message: [
    {
      content: { Str: "Summarize the attached document." },
      role: Role.User,
      variables: [],
    },
    {
      content: { Str: "Here is the summary of your document..." },
      role: Role.Assistant,
      variables: [],
    },
  ],
  system_instruction: [
    {
      content: { Str: "You are an expert summarizer." },
      role: Role.System || "system",
      variables: [],
    },
  ],
  model_settings: {
    GoogleChat: {
      labels: { project: "demo-gemini" },
      generation_config: {
        temperature: 0.5,
        top_p: 0.9,
        max_output_tokens: 256,
        stop_sequences: ["<END>"],
        response_modalities: ["Text"],
      },
      safety_settings: [
        {
          category: "HarmCategoryUnspecified",
          threshold: "BlockNone",
        },
      ],
    } as GeminiSettings,
  },
  model: "gemini-pro",
  provider: Provider.Gemini,
  version: "1.0.0",
  response_json_schema: undefined,
  parameters: ["summary", "document"],
  response_type: ResponseType.Score,
};
