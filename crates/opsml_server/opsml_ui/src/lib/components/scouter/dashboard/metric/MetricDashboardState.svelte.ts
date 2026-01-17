import type {
  BinnedDriftMap,
  MetricData,
  RecordCursor,
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
  getGenericMetricData,
  getServerDriftAlerts,
  getProfileFeatures,
  getSpcDriftMetrics,
  getPsiDriftMetrics,
  getCustomDriftMetrics,
} from "$lib/components/scouter/utils";
import type { BaseProfileDashboardState } from "../types";
import { DriftType } from "$lib/components/scouter/types";

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
  selectedTimeRange = $state<TimeRange | null>(null);
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
    this.selectedTimeRange = init.initialTimeRange;
    this.latestMetrics = init.initialMetrics;
    this.driftAlerts = init.initialAlerts;
    this.maxDataPoints = getMaxDataPoints();

    this.availableNames = getProfileFeatures(
      this.driftType,
      this.profile.profile
    );
    this.currentName = this.availableNames[0];

    if (this.latestMetrics) {
      this.currentMetricData = getGenericMetricData(
        this.latestMetrics,
        this.driftType as DriftType.Spc | DriftType.Psi | DriftType.Custom,
        this.currentName
      );
    }
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
      await Promise.all([this.loadMetrics(), this.loadAlerts()]);
    } finally {
      this.isUpdating = false;
    }
  }

  handleNameChange(name: string): void {
    this.currentName = name;
    if (this.latestMetrics) {
      this.currentMetricData = getGenericMetricData(
        this.latestMetrics,
        this.driftType as DriftType.Spc | DriftType.Psi | DriftType.Custom,
        this.currentName
      );
    }
  }

  async handleAlertPageChange(
    cursor: RecordCursor,
    direction: string
  ): Promise<void> {
    if (!this.selectedTimeRange) return;

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
    if (!this.selectedTimeRange) return;

    switch (this.driftType) {
      case DriftType.Spc:
        this.latestMetrics = await getSpcDriftMetrics(
          fetch,
          this.profiles,
          this.selectedTimeRange,
          this.maxDataPoints
        );
        break;
      case DriftType.Psi:
        this.latestMetrics = await getPsiDriftMetrics(
          fetch,
          this.profiles,
          this.selectedTimeRange,
          this.maxDataPoints
        );
        break;
      case DriftType.Custom:
        this.latestMetrics = await getCustomDriftMetrics(
          fetch,
          this.profiles,
          this.selectedTimeRange,
          this.maxDataPoints
        );
        break;
    }

    if (this.latestMetrics) {
      this.currentMetricData = getGenericMetricData(
        this.latestMetrics,
        this.driftType as DriftType.Spc | DriftType.Psi | DriftType.Custom,
        this.currentName
      );
    }
  }

  private async loadAlerts(): Promise<void> {
    if (!this.selectedTimeRange) return;

    this.driftAlerts = await getServerDriftAlerts(fetch, {
      uid: this.config.uid,
      active: true,
      start_datetime: this.selectedTimeRange.startTime,
      end_datetime: this.selectedTimeRange.endTime,
    });
  }
}
