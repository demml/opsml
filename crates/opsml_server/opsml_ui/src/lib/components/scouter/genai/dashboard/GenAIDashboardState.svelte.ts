import type {
  GenAIEvalConfig,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "../types";
import type { RecordCursor, MetricData, ServiceInfo } from "../../types";
import { type BinnedMetrics } from "../../custom/types";
import type { TimeRange } from "$lib/components/trace/types";
import { getMaxDataPoints } from "$lib/utils";
import {
  getGenAIEvalTaskDriftMetrics,
  getGenAIEvalWorkflowDriftMetrics,
  getServerGenAIEvalRecordPage,
  getServerGenAIEvalWorkflowPage,
} from "../utils";
import type { BaseProfileDashboardState } from "$lib/components/scouter/dashboard/types";

interface GenAIRangeCache {
  records: GenAIEvalRecordPaginationResponse;
  workflows: GenAIEvalWorkflowPaginationResponse;
  taskMetrics: BinnedMetrics;
  workflowMetrics: BinnedMetrics;
}

interface GenAIDashboardStateInit {
  config: GenAIEvalConfig;
  initialTimeRange: TimeRange;
  initialRecords: GenAIEvalRecordPaginationResponse;
  initialWorkflows: GenAIEvalWorkflowPaginationResponse;
  initialMetrics: { task: BinnedMetrics; workflow: BinnedMetrics };
}

export class GenAIDashboardState implements BaseProfileDashboardState {
  readonly config: GenAIEvalConfig;

  private readonly rangeCache = new Map<string, GenAIRangeCache>();

  isUpdating = $state(false);
  // not null because we always initialize with a time range
  selectedTimeRange = $state<TimeRange>(null!);
  maxDataPoints = $state<number>(0);

  evalRecords = $state<GenAIEvalRecordPaginationResponse | null>(null);
  evalWorkflows = $state<GenAIEvalWorkflowPaginationResponse | null>(null);

  taskMetrics = $state<BinnedMetrics | null>(null);
  workflowMetrics = $state<BinnedMetrics | null>(null);

  selectedMetricView = $state<"task" | "workflow">("task");
  currentMetricName = $state<string>("");

  constructor(init: GenAIDashboardStateInit) {
    this.config = init.config;
    this.maxDataPoints = getMaxDataPoints();
    this.selectedTimeRange = init.initialTimeRange;

    const initialKey = this.getRangeKey(init.initialTimeRange);
    this.cacheRangeData(initialKey, {
      records: init.initialRecords,
      workflows: init.initialWorkflows,
      taskMetrics: init.initialMetrics.task,
      workflowMetrics: init.initialMetrics.workflow,
    });
    this.applyCachedRange(initialKey);
  }

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
    if (newMaxDataPoints === this.maxDataPoints) return;
    this.maxDataPoints = newMaxDataPoints;
    if (this.selectedTimeRange) {
      await this.handleTimeRangeChange(this.selectedTimeRange);
    }
  }

  async handleTimeRangeChange(range: TimeRange): Promise<void> {
    if (this.isUpdating) return;
    this.isUpdating = true;

    try {
      this.selectedTimeRange = range;
      const rangeKey = this.getRangeKey(range);
      const cached = this.rangeCache.get(rangeKey);
      if (cached) {
        this.applyCachedRange(rangeKey);
        return;
      }

      const freshRange = await this.fetchRangeData(range);
      this.cacheRangeData(rangeKey, freshRange);
      this.applyCachedRange(rangeKey);
    } finally {
      this.isUpdating = false;
    }
  }

  async handleRecordPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    if (!this.selectedTimeRange) return;

    const response = await getServerGenAIEvalRecordPage(fetch, {
      service_info: this.getServiceInfo(),
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });

    this.evalRecords = response;
    this.updateCurrentRangeCache({ records: response });
  }

  async handleWorkflowPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    if (!this.selectedTimeRange) return;

    const response = await getServerGenAIEvalWorkflowPage(fetch, {
      service_info: this.getServiceInfo(),
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });

    this.evalWorkflows = response;
    this.updateCurrentRangeCache({ workflows: response });
  }

  handleMetricViewChange(view: "task" | "workflow"): void {
    if (this.selectedMetricView === view) return;
    this.selectedMetricView = view;
    this.ensureMetricName(view);
  }

  handleMetricNameChange(name: string): void {
    this.currentMetricName = name;
  }

  private getRangeKey(range: TimeRange): string {
    const start = range.startTime ?? "start";
    const end = range.endTime ?? "end";
    return `${start}-${end}-${this.maxDataPoints}`;
  }

  private cacheRangeData(key: string, data: GenAIRangeCache): void {
    this.rangeCache.set(key, data);
  }

  private applyCachedRange(key: string): void {
    const cached = this.rangeCache.get(key);
    if (!cached) return;

    this.evalRecords = cached.records;
    this.evalWorkflows = cached.workflows;
    this.taskMetrics = cached.taskMetrics;
    this.workflowMetrics = cached.workflowMetrics;
    this.ensureMetricName();
  }

  private ensureMetricName(view?: "task" | "workflow"): void {
    const metricView = view ?? this.selectedMetricView;
    const metrics =
      metricView === "task" ? this.taskMetrics : this.workflowMetrics;
    if (!metrics) {
      this.currentMetricName = "";
      return;
    }

    const availableNames = Object.keys(metrics.metrics);
    if (availableNames.length === 0) {
      this.currentMetricName = "";
      return;
    }

    if (
      !this.currentMetricName ||
      !availableNames.includes(this.currentMetricName)
    ) {
      this.currentMetricName = availableNames[0];
    }
  }

  private async fetchRangeData(range: TimeRange): Promise<GenAIRangeCache> {
    const serviceInfo = this.getServiceInfo();

    const [records, workflows, taskMetrics, workflowMetrics] =
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
          this.config.space,
          this.config.uid,
          range,
          this.maxDataPoints
        ),
        getGenAIEvalWorkflowDriftMetrics(
          fetch,
          this.config.space,
          this.config.uid,
          range,
          this.maxDataPoints
        ),
      ]);

    return {
      records,
      workflows,
      taskMetrics,
      workflowMetrics,
    };
  }

  private getServiceInfo(): ServiceInfo {
    return {
      space: this.config.space,
      uid: this.config.uid,
    };
  }

  private updateCurrentRangeCache(patch: Partial<GenAIRangeCache>): void {
    if (!this.selectedTimeRange) return;
    const key = this.getRangeKey(this.selectedTimeRange);
    const cached = this.rangeCache.get(key);
    if (!cached) return;

    this.rangeCache.set(key, { ...cached, ...patch });
  }
}
