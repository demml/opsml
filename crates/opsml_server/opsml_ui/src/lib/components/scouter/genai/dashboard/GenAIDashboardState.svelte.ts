import type {
  GenAIEvalConfig,
  GenAIEvalRecordPaginationResponse,
} from "../types";
import type {
  GenAIEvalWorkflowPaginationResponse,
  GenAIEvalTaskResponse,
} from "../types";
import type { RecordCursor, BinnedDriftMap, MetricData } from "../../types";
import type { TimeRange } from "$lib/components/trace/types";
import { getMaxDataPoints } from "$lib/utils";
import {
  getServerGenAIEvalRecordPage,
  getServerGenAIEvalWorkflowPage,
  getServerGenAIEvalTask,
} from "../utils";
import { loadGenAIMetrics } from "$lib/components/scouter/utils";
import {
  getCurrentMetricData,
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
}

export class GenAIDashboardState implements BaseProfileDashboardState {
  config: GenAIEvalConfig;
  profiles: DriftProfileResponse;
  isUpdating = $state(false);
  selectedTimeRange: TimeRange;
  maxDataPoints = $state<number>(0);

  evalRecords = $state<GenAIEvalRecordPaginationResponse | null>(null);
  selectedRecord = $state<string | null>(null);

  evalWorkflows = $state<GenAIEvalWorkflowPaginationResponse | null>(null);
  selectedWorkflow = $state<string | null>(null);

  workflowTasks = $state<GenAIEvalTaskResponse | null>(null);
  selectedTask = $state<string | null>(null);

  taskMetrics = $state<BinnedDriftMap | null>(null);
  workflowMetrics = $state<BinnedDriftMap | null>(null);
  selectedMetricView = $state<"task" | "workflow">("task");
  currentMetricName = $state<string>("");
  availableMetricNames = $state<string[]>([]);
  currentMetricData = $state<MetricData | null>(null);

  constructor(init: GenAIDashboardStateInit) {
    this.config = init.config;
    this.profiles = init.profiles;
    this.selectedTimeRange = $state(init.initialTimeRange);
    this.evalRecords = init.initialRecords;
    this.evalWorkflows = init.initialWorkflows;
    this.maxDataPoints = getMaxDataPoints();
  }

  async checkScreenSize(): Promise<void> {
    const newMaxDataPoints = getMaxDataPoints();
    if (newMaxDataPoints !== this.maxDataPoints) {
      this.maxDataPoints = newMaxDataPoints;
      if (this.selectedTimeRange) {
        await this.loadMetrics();
      }
    }
  }

  async handleTimeRangeChange(range: TimeRange): Promise<void> {
    if (this.isUpdating) return;
    this.isUpdating = true;

    try {
      this.selectedTimeRange = range;
      await this.loadAllData();
    } catch (error) {
      console.error("Failed to update time range:", error);
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
      service_info: {
        uid: this.config.uid,
        space: this.config.space,
      },
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
      service_info: {
        uid: this.config.uid,
        space: this.config.space,
      },
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }

  async handleRecordSelect(recordUid: string): Promise<void> {
    this.selectedRecord = recordUid;
    this.workflowTasks = await getServerGenAIEvalTask(fetch, {
      record_uid: recordUid,
    });
  }

  async handleWorkflowSelect(recordUid: string): Promise<void> {
    this.selectedWorkflow = recordUid;
    this.workflowTasks = await getServerGenAIEvalTask(fetch, {
      record_uid: recordUid,
    });
  }

  handleTaskSelect(taskId: string): void {
    this.selectedTask = taskId;
  }

  handleMetricViewChange(view: "task" | "workflow"): void {
    this.selectedMetricView = view;
    this.updateMetricData();
  }

  private updateMetricData(): void {
    const currentMetrics =
      this.selectedMetricView === "task"
        ? this.taskMetrics
        : this.workflowMetrics;

    if (!currentMetrics) return;

    const profile = this.profiles[DriftType.GenAI];
    if (!profile) return;

    this.availableMetricNames = getProfileFeatures(
      DriftType.GenAI,
      profile.profile
    );

    if (this.availableMetricNames.length > 0) {
      if (
        !this.currentMetricName ||
        !this.availableMetricNames.includes(this.currentMetricName)
      ) {
        this.currentMetricName = this.availableMetricNames[0];
      }

      this.currentMetricData = getCurrentMetricData(
        currentMetrics,
        DriftType.GenAI,
        this.currentMetricName
      );
    }
  }

  private async loadAllData(): Promise<void> {
    if (!this.selectedTimeRange) return;

    const [records, workflows, metrics] = await Promise.all([
      getServerGenAIEvalRecordPage(fetch, {
        service_info: {
          uid: this.config.uid,
          space: this.config.space,
        },
        start_datetime: this.selectedTimeRange.startTime,
        end_datetime: this.selectedTimeRange.endTime,
      }),
      getServerGenAIEvalWorkflowPage(fetch, {
        service_info: {
          uid: this.config.uid,
          space: this.config.space,
        },
        start_datetime: this.selectedTimeRange.startTime,
        end_datetime: this.selectedTimeRange.endTime,
      }),
      this.loadMetrics(),
    ]);

    this.evalRecords = records;
    this.evalWorkflows = workflows;
    this.selectedRecord = null;
    this.selectedWorkflow = null;
    this.workflowTasks = null;
    this.selectedTask = null;
  }

  private async loadMetrics(): Promise<void> {
    if (!this.selectedTimeRange) return;

    const { task, workflow } = await loadGenAIMetrics(
      fetch,
      this.profiles,
      this.selectedTimeRange,
      this.maxDataPoints
    );

    this.taskMetrics = task;
    this.workflowMetrics = workflow;
    this.updateMetricData();
  }
}
