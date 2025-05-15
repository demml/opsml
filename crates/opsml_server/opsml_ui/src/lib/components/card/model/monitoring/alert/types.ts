import type { DriftType } from "../types";

export interface DriftAlertRequest {
  name: string;
  space: string;
  version: string;
  limit_datetime?: string;
  active?: boolean;
  limit?: number;
}

export interface Alert {
  created_at: string;
  name: string;
  space: string;
  version: string;
  entity_name: string;
  alert: Record<string, string>;
  id: number;
  active: boolean;
  drift_type: string;
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
