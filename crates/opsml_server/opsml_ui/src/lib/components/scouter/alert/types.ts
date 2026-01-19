import type { DateTime } from "$lib/types";
import type { SpcDriftProfile } from "../spc/types";
import type { AlertThreshold, DriftType, RecordCursor } from "../types";

export interface DriftAlertPaginationRequest {
  uid: string;
  limit?: number;
  active?: boolean;
  cursor_created_at?: DateTime;
  cursor_id?: number;
  direction?: string;
  start_datetime?: DateTime;
  end_datetime?: DateTime;
}

export interface DriftAlertPaginationResponse {
  items: Alert[];
  has_next: boolean;
  next_cursor?: RecordCursor;
  has_previous: boolean;
  previous_cursor?: RecordCursor;
}

export interface ComparisonMetricAlert {
  metric_name: string;
  baseline_value: number;
  observed_value: number;
  delta: number | null;
  alert_threshold: AlertThreshold;
}

export interface PsiFeatureAlert {
  feature: string;
  drift: number;
  threshold: number;
}

export type SpcAlertType =
  | "OutOfBounds"
  | "Consecutive"
  | "Alternating"
  | "AllGood"
  | "Trend";

export type AlertZone = "Zone1" | "Zone2" | "Zone3" | "Zone4" | "NotApplicable";

export interface SpcAlertEntry {
  feature: string;
  kind: SpcAlertType;
  zone: AlertZone;
}

export type AlertMap = {
  [DriftType.Spc]: SpcAlertEntry;
  [DriftType.Psi]: PsiFeatureAlert;
  [DriftType.Custom]: ComparisonMetricAlert;
  [DriftType.GenAI]: ComparisonMetricAlert;
};

export interface Alert {
  created_at: string;
  entity_name: string;
  alert: AlertMap;
  id: number;
  active: boolean;
}
export interface AlertResponse {
  alerts: Alert[];
}

export interface UpdateAlertStatus {
  id: number;
  active: boolean;
  space: string;
}

export interface UpdateAlertResponse {
  updated: boolean;
}
