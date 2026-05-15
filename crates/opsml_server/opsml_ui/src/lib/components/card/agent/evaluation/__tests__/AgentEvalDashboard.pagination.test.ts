import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import AgentEvalDashboard from "../AgentEvalDashboard.svelte";
import type { AgentPromptEvalData } from "../types";
import type {
  AgentMonitoringPageData,
  AgentRefreshOptions,
} from "$lib/components/scouter/dashboard/utils";
import { Status } from "$lib/components/scouter/agent/types";
import { EntityType } from "$lib/components/scouter/types";

type SuccessfulAgentMonitoringPageData = Extract<
  AgentMonitoringPageData,
  { status: "success" }
>;

const refreshCalls = vi.hoisted(() => [] as unknown[]);

vi.mock("chart.js/auto", () => ({
  Chart: class {
    static register = vi.fn();
    destroy = vi.fn();
    resetZoom = vi.fn();
  },
}));
vi.mock("chart.js", () => ({ Filler: {} }));
vi.mock("chartjs-plugin-zoom", () => ({ default: {} }));
vi.mock("chartjs-plugin-annotation", () => ({ default: {} }));
vi.mock("chartjs-adapter-date-fns", () => ({}));

vi.mock("$lib/components/scouter/dashboard/utils", async () => {
  const actual = await vi.importActual<typeof import("$lib/components/scouter/dashboard/utils")>(
    "$lib/components/scouter/dashboard/utils",
  );
  return {
    ...actual,
    refreshAgentMonitoringData: vi.fn(async (
      _fetch: typeof globalThis.fetch,
      monitoringData: SuccessfulAgentMonitoringPageData,
      options: AgentRefreshOptions = {},
    ) => {
      refreshCalls.push(options);
      if (options.recordCursor) {
        monitoringData.selectedData = {
          ...monitoringData.selectedData,
          records: {
            items: [makeRecord("pagetwo2", 2, "2026-01-02T00:00:00Z")],
            has_next: false,
            has_previous: true,
            previous_cursor: { id: 2, created_at: "2026-01-02T00:00:00Z" },
          },
        };
      }
      if (options.workflowCursor) {
        monitoringData.selectedData = {
          ...monitoringData.selectedData,
          workflows: {
            items: [makeWorkflow(2, "workflow-record-page-2", "2026-01-02T00:00:00Z")],
            has_next: false,
            has_previous: true,
            previous_cursor: { id: 2, created_at: "2026-01-02T00:00:00Z" },
          },
        };
      }
    }),
  };
});

/** Builds a minimal evaluation record with cursor fields needed by pagination. */
function makeRecord(uid: string, id: number, createdAt: string) {
  return {
    record_id: `record-${id}`,
    created_at: createdAt,
    uid,
    context: {},
    id,
    updated_at: null,
    processing_started_at: null,
    processing_ended_at: null,
    processing_duration: null,
    entity_id: id,
    entity_uid: `entity-${id}`,
    status: Status.Processed,
    entity_type: EntityType.Agent,
    trace_id: `trace-${id}`,
  };
}

/** Builds a minimal workflow result with cursor fields needed by pagination. */
function makeWorkflow(id: number, recordUid: string, createdAt: string) {
  return {
    id,
    record_uid: recordUid,
    entity_id: id,
    entity_uid: `entity-${id}`,
    created_at: createdAt,
    total_tasks: 4,
    passed_tasks: 4,
    failed_tasks: 0,
    pass_rate: 1,
    duration_ms: 1200,
    execution_plan: { stages: [], nodes: {} },
  };
}

/** Builds dashboard props with one next-page cursor for records and workflows. */
function makeEvalData(): AgentPromptEvalData[] {
  return [
    {
      promptCard: {
        space: "default",
        name: "triage_prompt",
        version: "1.0.0",
      },
      monitoringData: {
        status: "success",
        uid: "eval-profile-1",
        registryType: "prompt",
        selectedTimeRange: {
          label: "Past 24 Hours",
          value: "24hours",
          startTime: "2026-01-01T00:00:00Z",
          endTime: "2026-01-02T00:00:00Z",
          bucketInterval: "1 hours",
        },
        profile: {
          config: {
            uid: "eval-profile-1",
            space: "default",
          },
        },
        selectedData: {
          metrics: { workflow: { metrics: {} } },
          driftAlerts: { items: [], has_next: false, has_previous: false },
          records: {
            items: [makeRecord("pageone1", 1, "2026-01-01T00:00:00Z")],
            has_next: true,
            next_cursor: { id: 1, created_at: "2026-01-01T00:00:00Z" },
            has_previous: false,
          },
          workflows: {
            items: [makeWorkflow(1, "workflow-record-page-1", "2026-01-01T00:00:00Z")],
            has_next: true,
            next_cursor: { id: 1, created_at: "2026-01-01T00:00:00Z" },
            has_previous: false,
          },
        },
      },
    } as unknown as AgentPromptEvalData,
  ];
}

describe("AgentEvalDashboard pagination", () => {
  beforeEach(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it("pages records with recordCursor and replaces visible record rows", async () => {
    refreshCalls.length = 0;
    render(AgentEvalDashboard, {
      props: {
        agentName: "support_agent",
        agentVersion: "1.0.0",
        agentPromptEvals: makeEvalData(),
      },
    });

    expect(screen.getByText("pageone1")).toBeInTheDocument();
    await fireEvent.click(screen.getByRole("button", { name: "Next evaluation records page" }));

    await waitFor(() => expect(screen.getByText("pagetwo2")).toBeInTheDocument());
    expect(refreshCalls).toEqual([
      { recordCursor: { cursor: { id: 1, created_at: "2026-01-01T00:00:00Z" }, direction: "next" } },
    ]);
    expect(screen.queryByText("pageone1")).not.toBeInTheDocument();
  });

  it("pages workflows with workflowCursor and does not send a record cursor", async () => {
    refreshCalls.length = 0;
    render(AgentEvalDashboard, {
      props: {
        agentName: "support_agent",
        agentVersion: "1.0.0",
        agentPromptEvals: makeEvalData(),
      },
    });

    expect(screen.getByText("workflow")).toBeInTheDocument();
    await fireEvent.click(screen.getByRole("button", { name: "Next workflow results page" }));

    await waitFor(() => {
      expect(refreshCalls).toEqual([
        { workflowCursor: { cursor: { id: 1, created_at: "2026-01-01T00:00:00Z" }, direction: "next" } },
      ]);
    });
    expect(refreshCalls[0]).not.toHaveProperty("recordCursor");
  });
});
