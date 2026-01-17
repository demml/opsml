import type {
  GenAIEvalConfig,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "../types";
import type { RecordCursor, MetricData } from "../../types";
import { type BinnedMetrics } from "../../custom/types";
import type { TimeRange } from "$lib/components/trace/types";
import { getMaxDataPoints } from "$lib/utils";
import {
  getServerGenAIEvalRecordPage,
  getServerGenAIEvalWorkflowPage,
} from "../utils";
import {
  getGenAITaskMetrics,
  getGenAIWorkflowMetrics,
  getProfileFeatures,
} from "$lib/components/scouter/utils";
import type { BaseProfileDashboardState } from "$lib/components/scouter/dashboard/types";
import type { DriftProfileResponse } from "$lib/components/scouter/utils";
import { DriftType } from "$lib/components/scouter/types";

interface GenAIDashboardStateInit {
  config: GenAIEvalConfig;
  profiles: DriftProfileResponse;
  initialTimeRange: TimeRange;
  initialRecords: GenAIEvalRecordPaginationResponse;
  initialWorkflows: GenAIEvalWorkflowPaginationResponse;
  initialMetrics: { task: BinnedMetrics; workflow: BinnedMetrics };
}

export class GenAIDashboardState implements BaseProfileDashboardState {
  readonly config: GenAIEvalConfig;
  readonly profiles: DriftProfileResponse;

  isUpdating = $state(false);
  selectedTimeRange = $state<TimeRange | null>(null);
  maxDataPoints = $state<number>(0);

  evalRecords = $state<GenAIEvalRecordPaginationResponse | null>(null);
  evalWorkflows = $state<GenAIEvalWorkflowPaginationResponse | null>(null);

  taskMetrics = $state<BinnedMetrics | null>(null);
  workflowMetrics = $state<BinnedMetrics | null>(null);

  selectedMetricView = $state<"task" | "workflow">("task");
  currentMetricName = $state<string>("");

  constructor(init: GenAIDashboardStateInit) {
    this.config = init.config;
    this.profiles = init.profiles;
    this.maxDataPoints = getMaxDataPoints();
    this.selectedTimeRange = init.initialTimeRange;
    this.evalRecords = init.initialRecords;
    this.evalWorkflows = init.initialWorkflows;
    this.taskMetrics = init.initialMetrics.task;
    this.workflowMetrics = init.initialMetrics.workflow;
    this.currentMetricName =
      Object.keys(init.initialMetrics.workflow.metrics)[0] || "";
  }

  /// get all keys from the current active type (task or workflow)
  get availableMetricNames(): string[] {
    const currentMetrics =
      this.selectedMetricView === "task"
        ? this.taskMetrics
        : this.workflowMetrics;
    return currentMetrics ? Object.keys(currentMetrics.metrics) : [];
  }

  get currentMetrics(): BinnedMetrics | null {
    return this.selectedMetricView === "task"
      ? this.taskMetrics
      : this.workflowMetrics;
  }

  get currentMetricData(): MetricData | null {
    if (!this.currentMetrics || !this.currentMetricName) return null;
    return this.currentMetrics.metrics[this.currentMetricName] || null;
  }

  async checkScreenSize(): Promise<void> {
    const newMaxDataPoints = getMaxDataPoints();
    if (newMaxDataPoints !== this.maxDataPoints) {
      this.maxDataPoints = newMaxDataPoints;
      if (this.selectedTimeRange) await this.loadMetrics();
    }
  }

  async handleTimeRangeChange(range: TimeRange): Promise<void> {
    if (this.isUpdating) return;
    this.isUpdating = true;

    try {
      this.selectedTimeRange = range;
      await this.loadAllData();
    } finally {
      this.isUpdating = false;
    }
  }

  async handleRecordPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    if (!this.selectedTimeRange) return;

    this.evalRecords = await getServerGenAIEvalRecordPage(fetch, {
      service_info: { uid: this.config.uid, space: this.config.space },
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }

  async handleWorkflowPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    if (!this.selectedTimeRange) return;

    this.evalWorkflows = await getServerGenAIEvalWorkflowPage(fetch, {
      service_info: { uid: this.config.uid, space: this.config.space },
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }

  handleMetricViewChange(view: "task" | "workflow"): void {
    this.selectedMetricView = view;
  }

  handleMetricNameChange(name: string): void {
    this.currentMetricName = name;
  }

  private async loadAllData(): Promise<void> {
    if (!this.selectedTimeRange) return;

    const [records, workflows] = await Promise.all([
      getServerGenAIEvalRecordPage(fetch, {
        service_info: { uid: this.config.uid, space: this.config.space },
        start_datetime: this.selectedTimeRange.startTime,
        end_datetime: this.selectedTimeRange.endTime,
      }),
      getServerGenAIEvalWorkflowPage(fetch, {
        service_info: { uid: this.config.uid, space: this.config.space },
        start_datetime: this.selectedTimeRange.startTime,
        end_datetime: this.selectedTimeRange.endTime,
      }),
      this.loadMetrics(),
    ]);

    this.evalRecords = records;
    this.evalWorkflows = workflows;
  }

  private async loadMetrics(): Promise<void> {
    if (!this.selectedTimeRange) return;

    const [task, workflow] = await Promise.all([
      getGenAITaskMetrics(
        fetch,
        this.profiles,
        this.selectedTimeRange,
        this.maxDataPoints
      ),
      getGenAIWorkflowMetrics(
        fetch,
        this.profiles,
        this.selectedTimeRange,
        this.maxDataPoints
      ),
    ]);

    this.taskMetrics = task;
    this.workflowMetrics = workflow;
  }
}
