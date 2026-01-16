import type {
  BinnedDriftMap,
  MetricData,
  RecordCursor,
  DriftType,
} from "$lib/components/scouter/types";
import type {
  DriftConfigType,
  UiProfile,
  DriftProfileResponse,
} from "$lib/components/scouter/utils";
import type { DriftAlertPaginationResponse } from "$lib/components/scouter/alert/types";
import type { TimeRange } from "$lib/components/trace/types";
import { getMaxDataPoints } from "$lib/utils";
import {
  getCurrentMetricData,
  getServerDriftAlerts,
  getProfileFeatures,
} from "$lib/components/scouter/utils";
import { loadMetricsForDriftType } from "$lib/components/scouter/utils";
import type { BaseProfileDashboardState } from "../types";

interface MetricDashboardStateInit {
  driftType: DriftType;
  profile: UiProfile;
  config: DriftConfigType;
  profiles: DriftProfileResponse;
  initialMetrics: BinnedDriftMap;
  initialTimeRange: TimeRange;
  initialAlerts: DriftAlertPaginationResponse;
}

export class MetricDashboardState implements BaseProfileDashboardState {
  driftType: DriftType;
  profile: UiProfile;
  config: DriftConfigType;
  profiles: DriftProfileResponse;
  isUpdating = $state(false);
  selectedTimeRange: TimeRange; // Remove null type
  maxDataPoints = $state<number>(0);

  currentName = $state<string>("");
  availableNames = $state<string[]>([]);
  latestMetrics = $state<BinnedDriftMap | null>(null);
  currentMetricData = $state<MetricData | null>(null);

  driftAlerts = $state<DriftAlertPaginationResponse | null>(null);

  constructor(init: MetricDashboardStateInit) {
    this.driftType = init.driftType;
    this.profile = init.profile;
    this.config = init.config;
    this.profiles = init.profiles;
    this.selectedTimeRange = $state(init.initialTimeRange);
    this.latestMetrics = init.initialMetrics;
    this.driftAlerts = init.initialAlerts;
    this.maxDataPoints = getMaxDataPoints();

    this.availableNames = getProfileFeatures(
      this.driftType,
      this.profile.profile
    );
    this.currentName = this.availableNames[0];
    this.currentMetricData = getCurrentMetricData(
      this.latestMetrics,
      this.driftType,
      this.currentName
    );
  }

  async checkScreenSize(): Promise<void> {
    const newMaxDataPoints = getMaxDataPoints();
    if (newMaxDataPoints !== this.maxDataPoints) {
      this.maxDataPoints = newMaxDataPoints;
      await this.loadMetrics();
    }
  }

  async handleTimeRangeChange(range: TimeRange): Promise<void> {
    if (this.isUpdating) return;
    this.isUpdating = true;

    try {
      this.selectedTimeRange = range;
      await Promise.all([this.loadMetrics(), this.loadAlerts()]);
    } catch (error) {
      console.error("Failed to update time range:", error);
    } finally {
      this.isUpdating = false;
    }
  }

  handleNameChange(name: string): void {
    this.currentName = name;
    if (this.latestMetrics) {
      this.currentMetricData = getCurrentMetricData(
        this.latestMetrics,
        this.driftType,
        this.currentName
      );
    }
  }

  async handleAlertPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    this.driftAlerts = await getServerDriftAlerts(fetch, {
      uid: this.config.uid,
      active: true,
      cursor_created_at: cursor.created_at,
      cursor_id: cursor.id,
      direction,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }

  private async loadMetrics(): Promise<void> {
    this.latestMetrics = await loadMetricsForDriftType(
      fetch,
      this.driftType,
      this.profiles,
      this.selectedTimeRange,
      this.maxDataPoints
    );

    if (this.latestMetrics) {
      this.currentMetricData = getCurrentMetricData(
        this.latestMetrics,
        this.driftType,
        this.currentName
      );
    }
  }

  private async loadAlerts(): Promise<void> {
    this.driftAlerts = await getServerDriftAlerts(fetch, {
      uid: this.config.uid,
      active: true,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }
}
