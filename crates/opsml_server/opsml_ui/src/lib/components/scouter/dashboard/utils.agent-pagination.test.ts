import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  type AgentMonitoringPageData,
  refreshAgentMonitoringData,
} from "./utils";
import type {
  AgentEvalWorkflowPaginationResponse,
  EvalRecordPaginationResponse,
} from "$lib/components/scouter/agent/types";

const agentPageCalls = vi.hoisted(() => ({
  records: [] as unknown[],
  workflows: [] as unknown[],
}));

vi.mock("$lib/components/scouter/agent/utils", async () => {
  const actual = await vi.importActual<typeof import("$lib/components/scouter/agent/utils")>(
    "$lib/components/scouter/agent/utils",
  );
  return {
    ...actual,
    getServerEvalRecordPage: vi.fn(async (_fetch, request) => {
      agentPageCalls.records.push(request);
      return makeRecordPage("record-next");
    }),
    getServerAgentEvalWorkflowPage: vi.fn(async (_fetch, request) => {
      agentPageCalls.workflows.push(request);
      return makeWorkflowPage("workflow-next");
    }),
  };
});

/** Builds the small pagination shape required by the dashboard refresh helper. */
function makeRecordPage(label: string): EvalRecordPaginationResponse {
  return {
    items: [{ record_id: label, id: 1, created_at: "2026-01-01T00:00:00Z" }],
    has_next: false,
    has_previous: false,
  } as unknown as EvalRecordPaginationResponse;
}

/** Builds the small workflow pagination shape required by the dashboard refresh helper. */
function makeWorkflowPage(label: string): AgentEvalWorkflowPaginationResponse {
  return {
    items: [{ workflow_id: label }],
    has_next: false,
    has_previous: false,
  } as unknown as AgentEvalWorkflowPaginationResponse;
}

/** Builds a successful agent monitoring payload with distinct record and workflow pages. */
function makeMonitoringData(): Extract<AgentMonitoringPageData, { status: "success" }> {
  return {
    status: "success",
    uid: "agent-card-uid",
    registryType: "agent",
    profile: {
      config: { uid: "eval-uid", space: "prod" },
    },
    selectedTimeRange: {
      label: "15m",
      value: "15min",
      startTime: "2026-01-01T00:00:00Z",
      endTime: "2026-01-01T00:15:00Z",
      bucketInterval: "1 minutes",
    },
    selectedData: {
      metrics: { task: {}, workflow: {} },
      driftAlerts: { items: [], has_next: false, has_previous: false },
      records: makeRecordPage("record-current"),
      workflows: makeWorkflowPage("workflow-current"),
    },
  } as unknown as Extract<AgentMonitoringPageData, { status: "success" }>;
}

describe("refreshAgentMonitoringData pagination", () => {
  beforeEach(() => {
    agentPageCalls.records.length = 0;
    agentPageCalls.workflows.length = 0;
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 1280 });
  });

  it("preserves workflows when paging records, then preserves records when paging workflows", async () => {
    const monitoringData = makeMonitoringData();
    const originalWorkflows = monitoringData.selectedData.workflows;

    await refreshAgentMonitoringData(vi.fn() as unknown as typeof fetch, monitoringData, {
      recordCursor: {
        cursor: { id: 7, created_at: "2026-01-01T00:01:00Z" },
        direction: "next",
      },
    });

    expect(agentPageCalls.records).toHaveLength(1);
    expect(agentPageCalls.workflows).toHaveLength(0);
    expect(monitoringData.selectedData.records.items[0].record_id).toBe("record-next");
    expect(monitoringData.selectedData.workflows).toBe(originalWorkflows);

    const pagedRecords = monitoringData.selectedData.records;

    await refreshAgentMonitoringData(vi.fn() as unknown as typeof fetch, monitoringData, {
      workflowCursor: {
        cursor: { id: 11, created_at: "2026-01-01T00:02:00Z" },
        direction: "previous",
      },
    });

    expect(agentPageCalls.records).toHaveLength(1);
    expect(agentPageCalls.workflows).toHaveLength(1);
    expect(monitoringData.selectedData.records).toBe(pagedRecords);
    expect(monitoringData.selectedData.workflows.items[0]).toMatchObject({
      workflow_id: "workflow-next",
    });
  });
});
