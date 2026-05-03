import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import SpanGenAiPanel from "../SpanGenAiPanel.svelte";
import type {
  GenAiSpanRecord,
  GenAiEvalResult,
} from "$lib/components/scouter/genai/types";

function makeSpan(overrides: Partial<GenAiSpanRecord> = {}): GenAiSpanRecord {
  return {
    trace_id: "trace-1",
    span_id: "span-1",
    service_name: "svc",
    start_time: "2026-01-01T00:00:00Z",
    end_time: "2026-01-01T00:00:01Z",
    duration_ms: 1000,
    status_code: 200,
    operation_name: "chat.completions",
    provider_name: "anthropic",
    request_model: "claude-3-5-sonnet",
    response_model: "claude-3-5-sonnet",
    response_id: null,
    input_tokens: 100,
    output_tokens: 50,
    cache_creation_input_tokens: null,
    cache_read_input_tokens: null,
    finish_reasons: ["end_turn"],
    output_type: null,
    conversation_id: null,
    agent_name: null,
    agent_id: null,
    agent_description: null,
    agent_version: null,
    data_source_id: null,
    tool_name: null,
    tool_type: null,
    tool_call_id: null,
    request_temperature: null,
    request_max_tokens: null,
    request_top_p: null,
    request_choice_count: null,
    request_seed: null,
    request_frequency_penalty: null,
    request_presence_penalty: null,
    request_stop_sequences: [],
    server_address: null,
    server_port: null,
    error_type: null,
    openai_api_type: null,
    openai_service_tier: null,
    label: null,
    entity_id: null,
    input_messages: null,
    output_messages: null,
    system_instructions: null,
    tool_definitions: null,
    eval_results: [],
    ...overrides,
  };
}

describe("SpanGenAiPanel", () => {
  it("renders all sub-tab buttons", () => {
    render(SpanGenAiPanel, { props: { span: makeSpan() } });
    for (const label of [
      "Messages",
      "Eval",
      "Request",
      "Agent",
      "Tool",
      "Server",
      "Raw",
    ]) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }
  });

  it("messages tab is default and shows empty-state when no message fields", () => {
    const { container } = render(SpanGenAiPanel, { props: { span: makeSpan() } });
    expect(container.textContent).toContain(
      "no message content captured for this span",
    );
  });

  it("renders parsed input messages on messages tab", () => {
    const span = makeSpan({
      input_messages: JSON.stringify([{ role: "user", content: "hello" }]),
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("input_messages");
    expect(container.textContent).toContain("user");
    expect(container.textContent).toContain("hello");
  });

  it("renders parsed output messages on messages tab", () => {
    const span = makeSpan({
      output_messages: JSON.stringify([
        { role: "assistant", content: "hi back" },
      ]),
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("output_messages");
    expect(container.textContent).toContain("assistant");
    expect(container.textContent).toContain("hi back");
  });

  it("renders system_instructions block", () => {
    const span = makeSpan({ system_instructions: "be helpful" });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("system_instructions");
    expect(container.textContent).toContain("be helpful");
  });

  it("falls back to <pre> on malformed input_messages json", () => {
    const span = makeSpan({ input_messages: "not json" });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("not json");
  });

  it("eval tab shows empty state when no eval_results", async () => {
    render(SpanGenAiPanel, { props: { span: makeSpan() } });
    await fireEvent.click(screen.getByRole("button", { name: "Eval" }));
    expect(
      screen.getByText("no eval_results recorded for this span"),
    ).toBeInTheDocument();
  });

  it("eval tab renders eval results when present", async () => {
    const ev: GenAiEvalResult = {
      name: "groundedness",
      score_label: "good",
      score_value: 0.8,
      explanation: "well-grounded",
      response_id: null,
    };
    const span = makeSpan({ eval_results: [ev] });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    await fireEvent.click(screen.getByRole("button", { name: "Eval" }));
    expect(container.textContent).toContain("groundedness");
    expect(container.textContent).toContain("well-grounded");
    expect(container.textContent).toContain("0.8");
  });

  it("params tab shows request_model and finish_reasons", async () => {
    render(SpanGenAiPanel, { props: { span: makeSpan() } });
    await fireEvent.click(screen.getByRole("button", { name: "Request" }));
    expect(screen.getByText("request_model")).toBeInTheDocument();
    expect(screen.getByText("finish_reasons")).toBeInTheDocument();
  });

  it("tool tab shows empty state when tool fields absent", async () => {
    render(SpanGenAiPanel, { props: { span: makeSpan() } });
    await fireEvent.click(screen.getByRole("button", { name: "Tool" }));
    expect(screen.getByText("no tool data for this span")).toBeInTheDocument();
  });

  it("tool tab renders tool fields when present", async () => {
    const span = makeSpan({
      tool_name: "search",
      tool_type: "function",
      tool_call_id: "call_1",
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    await fireEvent.click(screen.getByRole("button", { name: "Tool" }));
    expect(container.textContent).toContain("search");
    expect(container.textContent).toContain("call_1");
  });

  it("raw tab dumps the span json", async () => {
    const { container } = render(SpanGenAiPanel, { props: { span: makeSpan() } });
    await fireEvent.click(screen.getByRole("button", { name: "Raw" }));
    expect(container.textContent).toContain("span-1");
    expect(container.textContent).toContain("trace-1");
  });

  it("does not introduce internal overflow-y-auto", () => {
    const { container } = render(SpanGenAiPanel, {
      props: { span: makeSpan() },
    });
    expect(container.querySelector(".overflow-y-auto")).toBeNull();
  });

  it("does not include any dark: classes", () => {
    const span = makeSpan({
      input_messages: JSON.stringify([{ role: "user", content: "x" }]),
      tool_name: "t",
      eval_results: [
        {
          name: "n",
          score_label: null,
          score_value: null,
          explanation: null,
          response_id: null,
        },
      ],
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.innerHTML).not.toContain("dark:");
  });

  it("does not include text-gray-* classes", () => {
    const { container } = render(SpanGenAiPanel, {
      props: { span: makeSpan() },
    });
    expect(container.innerHTML).not.toMatch(/text-gray-\d+/);
  });
});
