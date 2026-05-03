export type MessageRole = "system" | "user" | "assistant" | "tool" | "developer" | "function";
export type Provider = "openai" | "anthropic" | "gemini" | "unknown";

export interface AnthropicContentBlock {
  type: "text" | "tool_use" | "tool_result" | "image";
  text?: string;
  name?: string;
  input?: unknown;
  content?: unknown;
}

export interface ChatMessage {
  role: MessageRole;
  content: string | AnthropicContentBlock[];
  name?: string;
  tool_call_id?: string;
}

export function detectProvider(provider_name: string | null): Provider {
  if (!provider_name) return "unknown";
  const p = provider_name.toLowerCase();
  if (p.includes("anthropic") || p.includes("claude")) return "anthropic";
  if (p.includes("openai") || p.includes("azure")) return "openai";
  if (p.includes("google") || p.includes("gemini") || p.includes("vertex")) {
    return "gemini";
  }
  return "unknown";
}

export function safeParseJson<T = unknown>(s: string | null): T | null {
  if (!s) return null;
  try {
    return JSON.parse(s) as T;
  } catch {
    return null;
  }
}

export function parseMessages(jsonStr: string | null): ChatMessage[] | null {
  const v = safeParseJson<
    ChatMessage[] | ChatMessage | { messages: ChatMessage[] }
  >(jsonStr);
  if (!v) return null;
  if (Array.isArray(v)) return v;
  if (
    typeof v === "object" &&
    v !== null &&
    "messages" in v &&
    Array.isArray((v as { messages: unknown }).messages)
  ) {
    return (v as { messages: ChatMessage[] }).messages;
  }
  if (typeof v === "object" && v !== null && "role" in v) {
    return [v as ChatMessage];
  }
  return null;
}

export function extractMessageRole(m: ChatMessage): MessageRole {
  return (m.role ?? "user") as MessageRole;
}

export function extractMessageText(m: ChatMessage): string {
  const c = m.content;
  if (typeof c === "string") return c;
  if (!Array.isArray(c)) return JSON.stringify(c, null, 2);
  const parts: string[] = [];
  for (const b of c as AnthropicContentBlock[]) {
    if (b.type === "text" && typeof b.text === "string") {
      parts.push(b.text);
    } else if (b.type === "tool_use") {
      parts.push(`[tool_use ${b.name ?? ""} ${JSON.stringify(b.input ?? {})}]`);
    } else if (b.type === "tool_result") {
      parts.push(`[tool_result ${JSON.stringify(b.content ?? "")}]`);
    } else if (b.type === "image") {
      parts.push(`[image]`);
    } else {
      parts.push(JSON.stringify(b));
    }
  }
  return parts.join("\n\n");
}
