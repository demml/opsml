import {
  DriftType,
  Status,
  type LLMDriftServerRecord,
  type LLMPageResponse,
  type PaginationCursor,
} from "../types";
import { AlertThreshold } from "./llm";
import { type BinnedMetrics } from "../types";
import {
  type Prompt,
  Provider,
  Role,
  ResponseType,
} from "$lib/components/genai/types";
import type { LLMDriftProfile } from "./llm";
import type { OpenAIChatSettings } from "$lib/components/genai/settings/openai";
import type { GeminiSettings } from "$lib/components/genai/settings/gemini";

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
      role: Role.Assistant || "system",
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

/**
 * Mock LLMDriftProfile for UI development and testing.
 * Includes realistic metrics, config, and alert conditions for LLM drift monitoring.
 */
export const mockLLMDriftProfile: LLMDriftProfile = {
  metrics: [
    {
      name: "toxicity_score",
      value: 0.12,
      prompt: mockOpenAIPrompt,
      alert_condition: {
        alert_threshold: AlertThreshold.Above,
        alert_threshold_value: 0.1,
      },
    },
    {
      name: "coherence_score",
      value: 0.85,
      prompt: mockGeminiPrompt,
      alert_condition: {
        alert_threshold: AlertThreshold.Below,
        alert_threshold_value: 0.8,
      },
    },
  ],
  metric_names: ["toxicity_score", "coherence_score"],
  config: {
    sample_rate: 50,
    space: "llm-services",
    name: "summarizer",
    version: "3.0.0",
    drift_type: DriftType.LLM,
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#llm-alerts" },
      },
      schedule: "0 */2 * * *", // Every 2 hours
      alert_conditions: {
        toxicity_score: {
          alert_threshold: AlertThreshold.Above,
          alert_threshold_value: 0.1,
        },
        coherence_score: {
          alert_threshold: AlertThreshold.Below,
          alert_threshold_value: 0.8,
        },
      },
    },
  },
  scouter_version: "2.0.0",
};

export const mockLLMMetrics: BinnedMetrics = {
  metrics: {
    toxicity_score: {
      metric: "toxicity_score",
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      stats: [
        {
          avg: 0.95,
          lower_bound: 0.92,
          upper_bound: 0.98,
        },
        {
          avg: 0.94,
          lower_bound: 0.91,
          upper_bound: 0.97,
        },
        {
          avg: 0.96,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.9,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.4,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
      ],
    },
    coherence_score: {
      metric: "coherence_score",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 0.88,
          lower_bound: 0.85,
          upper_bound: 0.91,
        },
        {
          avg: 0.87,
          lower_bound: 0.84,
          upper_bound: 0.9,
        },
        {
          avg: 0.89,
          lower_bound: 0.86,
          upper_bound: 0.92,
        },
      ],
    },
  },
};

function randomStatus(): Status {
  const statuses = [
    Status.Pending,
    Status.Processing,
    Status.Processed,
    Status.Failed,
  ];
  return statuses[Math.floor(Math.random() * statuses.length)];
}

function randomDate(offsetDays: number = 0): string {
  const date = new Date();
  date.setDate(date.getDate() - offsetDays);
  return date.toISOString();
}

export const mockLLMDriftServerRecords: LLMDriftServerRecord[] = Array.from(
  { length: 30 },
  (_, i) => ({
    created_at: randomDate(30 - i),
    space: `space_${(i % 5) + 1}`,
    name: `card_${(i % 10) + 1}`,
    version: `v${(i % 3) + 1}.0.${i}`,
    prompt: i % 2 === 0 ? `Prompt for card_${(i % 10) + 1}` : undefined,
    context: `Context for card_${(i % 10) + 1}`,
    status: randomStatus(),
    id: i + 1,
    uid: `uid_${i + 1}`,
    score: {
      relevance: {
        score: Number(Math.random().toFixed(2)),
        reason:
          "The prompt is relevant and you should use it!. AHHHHHHHHHHHHHHHHHHHHHHHHH",
      },
      coherence: {
        score: Number(Math.random().toFixed(2)),
        reason: "Sample reason",
      },
    },
    updated_at: randomDate(29 - i),
    processing_started_at: i % 3 === 0 ? randomDate(30 - i) : undefined,
    processing_ended_at: i % 4 === 0 ? randomDate(29 - i) : undefined,
    processing_duration:
      i % 5 === 0 ? Math.floor(Math.random() * 60) : undefined,
  })
);

let paginationCursor: PaginationCursor = {
  id: mockLLMDriftServerRecords.length,
};
export const mockLLMDriftPageResponse: LLMPageResponse = {
  items: mockLLMDriftServerRecords,
  next_cursor: paginationCursor,
  has_more: true,
};
