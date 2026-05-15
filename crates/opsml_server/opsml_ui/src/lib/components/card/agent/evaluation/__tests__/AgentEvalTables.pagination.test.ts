import { fireEvent, render, screen } from "@testing-library/svelte";
import { describe, expect, it, vi } from "vitest";
import AgentEvalRecordTable from "../AgentEvalRecordTable.svelte";
import AgentEvalWorkflowTable from "../AgentEvalWorkflowTable.svelte";
import type { RecordWithAgent, WorkflowWithAgent } from "../types";

const record = {
  _agentName: "triage_prompt",
  _evalPath: "/opsml/prompt/card/default/triage/1.0.0/evaluation",
  record_id: "record-a",
  created_at: "2026-01-01T00:00:00Z",
  uid: "record-uid-a",
  context: {},
  id: 1,
  updated_at: null,
  processing_started_at: null,
  processing_ended_at: null,
  processing_duration: null,
  entity_id: 1,
  entity_uid: "entity-a",
  status: "Processed",
  entity_type: "Agent",
  trace_id: "trace-a",
} as RecordWithAgent;

const workflow = {
  _agentName: "triage_prompt",
  _evalPath: "/opsml/prompt/card/default/triage/1.0.0/evaluation",
  _profile: {} as WorkflowWithAgent["_profile"],
  _traceId: "trace-a",
  id: 1,
  record_uid: "record-uid-a",
  entity_id: 1,
  entity_uid: "entity-a",
  created_at: "2026-01-01T00:00:00Z",
  total_tasks: 4,
  passed_tasks: 4,
  failed_tasks: 0,
  pass_rate: 1,
  duration_ms: 1200,
  execution_plan: { stages: [], nodes: {} },
} as WorkflowWithAgent;

describe("Agent eval pagination tables", () => {
  it("emits record pagination directions only when controls are enabled", async () => {
    const onPageChange = vi.fn();
    render(AgentEvalRecordTable, {
      props: {
        records: [record],
        hasNext: true,
        hasPrevious: false,
        onPageChange,
      },
    });

    await fireEvent.click(screen.getByRole("button", { name: "Next evaluation records page" }));
    await fireEvent.click(screen.getByRole("button", { name: "Previous evaluation records page" }));

    expect(onPageChange).toHaveBeenCalledTimes(1);
    expect(onPageChange).toHaveBeenCalledWith("next");
  });

  it("emits workflow pagination directions only when controls are enabled", async () => {
    const onPageChange = vi.fn();
    render(AgentEvalWorkflowTable, {
      props: {
        workflows: [workflow],
        hasNext: false,
        hasPrevious: true,
        onPageChange,
      },
    });

    await fireEvent.click(screen.getByRole("button", { name: "Next workflow results page" }));
    await fireEvent.click(screen.getByRole("button", { name: "Previous workflow results page" }));

    expect(onPageChange).toHaveBeenCalledTimes(1);
    expect(onPageChange).toHaveBeenCalledWith("previous");
  });
});
