import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
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
  it("renders provider/model header chips", () => {
    const { container } = render(SpanGenAiPanel, { props: { span: makeSpan() } });
    expect(container.textContent).toContain("anthropic");
    expect(container.textContent).toContain("claude-3-5-sonnet");
  });

  it("hides Input/Output/System/Tool/Evals when their fields are absent", () => {
    render(SpanGenAiPanel, { props: { span: makeSpan() } });
    expect(screen.queryByText("Input")).toBeNull();
    expect(screen.queryByText("Output")).toBeNull();
    expect(screen.queryByText("System")).toBeNull();
    expect(screen.queryByText("Tool")).toBeNull();
    expect(screen.queryByText("Evals")).toBeNull();
  });

  it("renders parsed input messages with role badges", () => {
    const span = makeSpan({
      input_messages: JSON.stringify([
        { role: "user", content: "hello" },
      ]),
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("Input")).toBeInTheDocument();
    expect(container.textContent).toContain("user");
    expect(container.textContent).toContain("hello");
  });

  it("renders parsed output messages", () => {
    const span = makeSpan({
      output_messages: JSON.stringify([
        { role: "assistant", content: "hi back" },
      ]),
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("Output")).toBeInTheDocument();
    expect(container.textContent).toContain("assistant");
    expect(container.textContent).toContain("hi back");
  });

  it("falls back to raw <pre> for malformed input_messages json", () => {
    const span = makeSpan({ input_messages: "not json" });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("Input")).toBeInTheDocument();
    expect(container.textContent).toContain("not json");
  });

  it("renders system instructions block", () => {
    const span = makeSpan({ system_instructions: JSON.stringify("be helpful") });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("System")).toBeInTheDocument();
    expect(container.textContent).toContain("be helpful");
  });

  it("renders tool block when tool_name set", () => {
    const span = makeSpan({
      tool_name: "search",
      tool_type: "function",
      tool_call_id: "call_1",
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("Tool")).toBeInTheDocument();
    expect(container.textContent).toContain("search");
    expect(container.textContent).toContain("call_1");
  });

  it("renders eval results", () => {
    const ev: GenAiEvalResult = {
      name: "groundedness",
      score_label: "good",
      score_value: 0.8,
      explanation: "well-grounded",
      response_id: null,
    };
    const span = makeSpan({ eval_results: [ev] });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("Evals")).toBeInTheDocument();
    expect(container.textContent).toContain("groundedness");
    expect(container.textContent).toContain("well-grounded");
  });

  it("renders arrow model label when request and response models differ", () => {
    const span = makeSpan({
      request_model: "claude-3-opus",
      response_model: "claude-3-5-sonnet",
    });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("claude-3-opus → claude-3-5-sonnet");
  });

  it("renders dash when both models are null", () => {
    const span = makeSpan({ request_model: null, response_model: null });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("—");
  });

  it("renders integer score via fmtInt for score_value > 1", () => {
    const ev: GenAiEvalResult = {
      name: "relevance",
      score_label: null,
      score_value: 5,
      explanation: null,
      response_id: null,
    };
    const span = makeSpan({ eval_results: [ev] });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("relevance");
    expect(container.textContent).toContain("5");
  });

  it("renders percentage score via fmtPct for negative score_value within [-1,0]", () => {
    const ev: GenAiEvalResult = {
      name: "accuracy",
      score_label: null,
      score_value: -0.3,
      explanation: null,
      response_id: null,
    };
    const span = makeSpan({ eval_results: [ev] });
    const { container } = render(SpanGenAiPanel, { props: { span } });
    expect(container.textContent).toContain("accuracy");
  });

  it("renders no score chip when score_value is null", () => {
    const ev: GenAiEvalResult = {
      name: "check",
      score_label: null,
      score_value: null,
      explanation: null,
      response_id: null,
    };
    const span = makeSpan({ eval_results: [ev] });
    render(SpanGenAiPanel, { props: { span } });
    expect(screen.getByText("check")).toBeInTheDocument();
  });

  it("does not introduce internal overflow-y-auto", () => {
    const { container } = render(SpanGenAiPanel, { props: { span: makeSpan() } });
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
});
