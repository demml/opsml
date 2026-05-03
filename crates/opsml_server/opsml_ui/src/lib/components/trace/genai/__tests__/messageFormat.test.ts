import { describe, it, expect } from "vitest";
import {
  detectProvider,
  safeParseJson,
  parseMessages,
  extractMessageText,
  type ChatMessage,
  type AnthropicContentBlock,
} from "../messageFormat";

describe("detectProvider", () => {
  it("identifies openai variants", () => {
    expect(detectProvider("openai")).toBe("openai");
    expect(detectProvider("OpenAI")).toBe("openai");
    expect(detectProvider("azure")).toBe("openai");
  });

  it("identifies anthropic variants", () => {
    expect(detectProvider("Anthropic")).toBe("anthropic");
    expect(detectProvider("claude-3-5-sonnet")).toBe("anthropic");
  });

  it("identifies gemini variants", () => {
    expect(detectProvider("google")).toBe("gemini");
    expect(detectProvider("gemini")).toBe("gemini");
    expect(detectProvider("vertex")).toBe("gemini");
  });

  it("returns unknown for null and unrecognized", () => {
    expect(detectProvider(null)).toBe("unknown");
    expect(detectProvider("mistral")).toBe("unknown");
  });
});

describe("safeParseJson", () => {
  it("parses valid json", () => {
    expect(safeParseJson<{ a: number }>('{"a":1}')).toEqual({ a: 1 });
  });

  it("returns null for invalid json", () => {
    expect(safeParseJson("not json")).toBeNull();
  });

  it("returns null for null input", () => {
    expect(safeParseJson(null)).toBeNull();
  });
});

describe("parseMessages", () => {
  it("parses array form", () => {
    const arr: ChatMessage[] = [{ role: "user", content: "hi" }];
    expect(parseMessages(JSON.stringify(arr))).toEqual(arr);
  });

  it("parses { messages: [...] } wrapper form", () => {
    const arr: ChatMessage[] = [{ role: "assistant", content: "hello" }];
    expect(parseMessages(JSON.stringify({ messages: arr }))).toEqual(arr);
  });

  it("parses single object form", () => {
    const m: ChatMessage = { role: "system", content: "be nice" };
    expect(parseMessages(JSON.stringify(m))).toEqual([m]);
  });

  it("returns null for garbage", () => {
    expect(parseMessages("garbage")).toBeNull();
    expect(parseMessages(null)).toBeNull();
  });

  it("returns null for object without role or messages key", () => {
    expect(parseMessages('{"foo":1}')).toBeNull();
  });
});

describe("extractMessageText", () => {
  it("returns string content as-is", () => {
    const m: ChatMessage = { role: "user", content: "hello world" };
    expect(extractMessageText(m)).toBe("hello world");
  });

  it("concatenates anthropic text blocks with double newline", () => {
    const blocks: AnthropicContentBlock[] = [
      { type: "text", text: "first" },
      { type: "text", text: "second" },
    ];
    const m: ChatMessage = { role: "assistant", content: blocks };
    expect(extractMessageText(m)).toBe("first\n\nsecond");
  });

  it("formats tool_use blocks", () => {
    const blocks: AnthropicContentBlock[] = [
      { type: "tool_use", name: "search", input: { query: "x" } },
    ];
    const m: ChatMessage = { role: "assistant", content: blocks };
    expect(extractMessageText(m)).toBe(
      '[tool_use search {"query":"x"}]',
    );
  });

  it("formats tool_result blocks", () => {
    const blocks: AnthropicContentBlock[] = [
      { type: "tool_result", content: "ok" },
    ];
    const m: ChatMessage = { role: "tool", content: blocks };
    expect(extractMessageText(m)).toBe('[tool_result "ok"]');
  });

  it("formats image blocks", () => {
    const blocks: AnthropicContentBlock[] = [{ type: "image" }];
    const m: ChatMessage = { role: "user", content: blocks };
    expect(extractMessageText(m)).toBe("[image]");
  });

  it("falls back to JSON.stringify for unknown blocks", () => {
    const blocks = [{ type: "weird" } as unknown as AnthropicContentBlock];
    const m: ChatMessage = { role: "user", content: blocks };
    expect(extractMessageText(m)).toBe('{"type":"weird"}');
  });

  it("stringifies non-array non-string content", () => {
    const m = { role: "user", content: { foo: 1 } } as unknown as ChatMessage;
    expect(extractMessageText(m)).toBe('{\n  "foo": 1\n}');
  });
});
