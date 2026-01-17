// $lib/components/scouter/genai/dashboard/genai.svelte.ts
import {
  getServerGenAIEvalRecordPage,
  getServerGenAIEvalWorkflowPage,
  getGenAIEvalTaskDriftMetrics,
  getGenAIEvalWorkflowDriftMetrics,
} from "../utils";
import type { DashboardContext } from "../../dashboard/dashboard.svelte";
import type {
  GenAIEvalConfig,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "../types";
import type { BinnedMetrics } from "../../custom/types";
import type { RecordCursor } from "../../types";

interface GenAIStoreProps {
  config: GenAIEvalConfig;
  ctx: DashboardContext; // Injected dependency
  initialData: {
    records: GenAIEvalRecordPaginationResponse;
    workflows: GenAIEvalWorkflowPaginationResponse;
    metrics: { task: BinnedMetrics; workflow: BinnedMetrics };
  };
}

export function createGenAIStore({
  config,
  ctx,
  initialData,
}: GenAIStoreProps) {
  // -- State --
  let isLoading = $state(false);
  let records = $state(initialData.records);
  let workflows = $state(initialData.workflows);
  let taskMetrics = $state(initialData.metrics.task);
  let workflowMetrics = $state(initialData.metrics.workflow);
  let selectedMetricView = $state<"task" | "workflow">("workflow");
  let currentMetricName = $state<string>("");

  const currentMetricsObj = $derived(
    selectedMetricView === "task" ? taskMetrics : workflowMetrics
  );

  const availableMetricNames = $derived(
    currentMetricsObj ? Object.keys(currentMetricsObj.metrics) : []
  );

  const currentMetricData = $derived(
    currentMetricsObj && currentMetricName
      ? currentMetricsObj.metrics[currentMetricName]
      : null
  );

  // -- Effects --

  // 1. React to TimeRange or Screen Size changes automatically
  $effect(() => {
    const range = ctx.timeRange;
    const points = ctx.maxDataPoints;

    fetchAll(range, points);
  });

  // 2. Ensure a valid metric name is selected
  $effect(() => {
    if (
      availableMetricNames.length > 0 &&
      !availableMetricNames.includes(currentMetricName)
    ) {
      currentMetricName = availableMetricNames[0];
    }
  });

  // -- Actions --

  async function fetchAll(range: typeof ctx.timeRange, maxPoints: number) {
    isLoading = true;
    try {
      const serviceInfo = { uid: config.uid, space: config.space };

      // Parallel Fetch
      const [newRecords, newWorkflows, newTaskMetrics, newWorkflowMetrics] =
        await Promise.all([
          getServerGenAIEvalRecordPage(fetch, {
            service_info: serviceInfo,
            start_datetime: range.startTime,
            end_datetime: range.endTime,
          }),
          getServerGenAIEvalWorkflowPage(fetch, {
            service_info: serviceInfo,
            start_datetime: range.startTime,
            end_datetime: range.endTime,
          }),
          getGenAIEvalTaskDriftMetrics(
            fetch,
            config.space,
            config.uid,
            range,
            maxPoints
          ),
          getGenAIEvalWorkflowDriftMetrics(
            fetch,
            config.space,
            config.uid,
            range,
            maxPoints
          ),
        ]);

      records = newRecords;
      workflows = newWorkflows;
      taskMetrics = newTaskMetrics;
      workflowMetrics = newWorkflowMetrics;
    } catch (e) {
      console.error("Failed to refresh GenAI data", e);
    } finally {
      isLoading = false;
    }
  }

  async function handleRecordPageChange(
    cursor: RecordCursor,
    direction: string
  ) {
    const response = await getServerGenAIEvalRecordPage(fetch, {
      service_info: { uid: config.uid, space: config.space },
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: ctx.timeRange.startTime,
      end_datetime: ctx.timeRange.endTime,
    });
    records = response;
  }

  async function handleWorkflowPageChange(
    cursor: RecordCursor,
    direction: string
  ) {
    const response = await getServerGenAIEvalWorkflowPage(fetch, {
      service_info: { uid: config.uid, space: config.space },
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: ctx.timeRange.startTime,
      end_datetime: ctx.timeRange.endTime,
    });
    workflows = response;
  }

  return {
    get isLoading() {
      return isLoading;
    },
    get records() {
      return records;
    },
    get workflows() {
      return workflows;
    },
    get selectedMetricView() {
      return selectedMetricView;
    },
    set selectedMetricView(v) {
      selectedMetricView = v;
    },
    get currentMetricName() {
      return currentMetricName;
    },
    set currentMetricName(v) {
      currentMetricName = v;
    },
    get availableMetricNames() {
      return availableMetricNames;
    },
    get currentMetricData() {
      return currentMetricData;
    },
    handleRecordPageChange,
    handleWorkflowPageChange,
  };
}
