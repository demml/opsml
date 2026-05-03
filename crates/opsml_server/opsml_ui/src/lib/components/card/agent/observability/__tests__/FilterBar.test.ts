import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import FilterBar from "../FilterBar.svelte";
import type { AppliedFilters, AvailableFilters } from "../types";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const AVAILABLE: AvailableFilters = {
  agents: [
    {
      agent_name: "planner",
      agent_id: null,
      conversation_id: null,
      span_count: 5,
      total_input_tokens: 1000,
      total_output_tokens: 500,
      last_seen: null,
    },
    {
      agent_name: "executor",
      agent_id: null,
      conversation_id: null,
      span_count: 3,
      total_input_tokens: 800,
      total_output_tokens: 400,
      last_seen: null,
    },
  ],
  providers: ["openai", "anthropic"],
  models: ["gpt-4o", "claude-3-5-sonnet"],
  operations: ["chat.completions", "embeddings"],
};

const BASE_APPLIED: AppliedFilters = {
  service_name: "space:name",
  entity_id: null,
  agent_name: null,
  model: null,
  provider_name: null,
  operation_name: null,
  start_time: "2026-01-01T00:00:00Z" as unknown as AppliedFilters["start_time"],
  end_time: "2026-01-02T00:00:00Z" as unknown as AppliedFilters["end_time"],
  bucket_interval: "hour",
};

const EVAL_PROFILES = [
  { uid: "abc-123", alias: "v1", name: "my-profile" },
  { uid: "def-456", alias: null, name: "other-profile" },
];

async function selectOption(triggerLabel: string, optionLabel: string) {
  await fireEvent.click(screen.getByRole("button", { name: triggerLabel }));
  await fireEvent.click(screen.getByRole("option", { name: optionLabel }));
}

// ── (1) onChange fires with correct delta ─────────────────────────────────────

describe("FilterBar — (1) filter state update: onChange fires with correct delta", () => {
  it("model selection emits full delta with updated model, others null", async () => {
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange } });
    await selectOption("Model", "gpt-4o");
    expect(onChange).toHaveBeenCalledOnce();
    expect(onChange).toHaveBeenCalledWith({
      model: "gpt-4o",
      agent_name: null,
      provider_name: null,
      operation_name: null,
      entity_id: null,
    });
  });

  it("agent selection emits full delta with updated agent_name", async () => {
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange } });
    await selectOption("Agent", "planner");
    expect(onChange).toHaveBeenCalledWith({
      agent_name: "planner",
      model: null,
      provider_name: null,
      operation_name: null,
      entity_id: null,
    });
  });

  it("provider selection emits full delta with updated provider_name", async () => {
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange } });
    await selectOption("Provider", "anthropic");
    expect(onChange).toHaveBeenCalledWith({
      agent_name: null,
      model: null,
      provider_name: "anthropic",
      operation_name: null,
      entity_id: null,
    });
  });

  it("operation selection emits full delta with updated operation_name", async () => {
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange } });
    await selectOption("Operation", "chat.completions");
    expect(onChange).toHaveBeenCalledWith({
      agent_name: null,
      model: null,
      provider_name: null,
      operation_name: "chat.completions",
      entity_id: null,
    });
  });

  it("profile selection emits full delta with updated entity_id", async () => {
    const onChange = vi.fn();
    render(FilterBar, {
      props: { available: AVAILABLE, applied: BASE_APPLIED, evalProfiles: EVAL_PROFILES, onChange },
    });
    await selectOption("Profile", "v1");
    expect(onChange).toHaveBeenCalledWith({
      agent_name: null,
      model: null,
      provider_name: null,
      operation_name: null,
      entity_id: "abc-123",
    });
  });

  it("selecting 'all' emits null for that field (clear filter)", async () => {
    const applied: AppliedFilters = { ...BASE_APPLIED, model: "gpt-4o" };
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied, onChange } });
    await selectOption("Model", "all");
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ model: null }),
    );
  });

  it("changing one filter does not clobber other active filters", async () => {
    const applied: AppliedFilters = { ...BASE_APPLIED, model: "gpt-4o", agent_name: "planner" };
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied, onChange } });
    await selectOption("Provider", "openai");
    const delta = onChange.mock.calls[0][0];
    expect(delta.model).toBe("gpt-4o");
    expect(delta.agent_name).toBe("planner");
    expect(delta.provider_name).toBe("openai");
  });
});

// ── (2) Refetch trigger: onChange fires exactly once per selection ─────────────

describe("FilterBar — (2) refetch trigger: onChange fires once per selection", () => {
  it("each dropdown selection triggers onChange exactly once", async () => {
    const onChange = vi.fn();
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange } });
    await selectOption("Model", "gpt-4o");
    await selectOption("Agent", "executor");
    await selectOption("Provider", "openai");
    expect(onChange).toHaveBeenCalledTimes(3);
  });
});

// ── (3) Active filter displayed on trigger immediately ────────────────────────

describe("FilterBar — (3) active filter displayed on trigger immediately", () => {
  it("Model trigger shows selected value immediately after click", async () => {
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange: vi.fn() } });
    await selectOption("Model", "claude-3-5-sonnet");
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent("claude-3-5-sonnet");
  });

  it("Agent trigger shows selected value immediately after click", async () => {
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange: vi.fn() } });
    await selectOption("Agent", "executor");
    expect(screen.getByRole("button", { name: "Agent" })).toHaveTextContent("executor");
  });

  it("Provider trigger shows selected value immediately after click", async () => {
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange: vi.fn() } });
    await selectOption("Provider", "openai");
    expect(screen.getByRole("button", { name: "Provider" })).toHaveTextContent("openai");
  });

  it("Operation trigger shows selected value immediately after click", async () => {
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange: vi.fn() } });
    await selectOption("Operation", "embeddings");
    expect(screen.getByRole("button", { name: "Operation" })).toHaveTextContent("embeddings");
  });

  it("trigger reverts to 'all' after clearing filter", async () => {
    const applied: AppliedFilters = { ...BASE_APPLIED, model: "gpt-4o" };
    render(FilterBar, { props: { available: AVAILABLE, applied, onChange: vi.fn() } });
    await selectOption("Model", "all");
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent("all");
  });
});

// ── Profile dropdown visibility + lock ───────────────────────────────────────

describe("FilterBar — Profile dropdown", () => {
  it("Profile dropdown not rendered when evalProfiles is empty", () => {
    render(FilterBar, { props: { available: AVAILABLE, applied: BASE_APPLIED, onChange: vi.fn() } });
    expect(screen.queryByRole("button", { name: "Profile" })).not.toBeInTheDocument();
  });

  it("Profile dropdown renders when evalProfiles provided", () => {
    render(FilterBar, {
      props: {
        available: AVAILABLE,
        applied: BASE_APPLIED,
        evalProfiles: EVAL_PROFILES,
        onChange: vi.fn(),
      },
    });
    expect(screen.getByRole("button", { name: "Profile" })).toBeInTheDocument();
  });

  it("Profile dropdown is disabled when lockEntity=true", async () => {
    const onChange = vi.fn();
    render(FilterBar, {
      props: {
        available: AVAILABLE,
        applied: { ...BASE_APPLIED, entity_id: "abc-123" },
        evalProfiles: EVAL_PROFILES,
        lockEntity: true,
        onChange,
      },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    expect(onChange).not.toHaveBeenCalled();
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });
});
