import type { DateTime } from "$lib/types";
import type { RecordCursor } from "../types";

export interface DriftAlertPaginationRequest {
  uid: string;
  limit?: number;
  active?: boolean;
  cursor_created_at?: DateTime;
  cursor_id?: number;
  direction?: "next" | "previous";
}

export interface DriftAlertPaginationResponse {
  items: Alert[];
  has_next: boolean;
  next_cursor?: RecordCursor;
  has_previous: boolean;
  previous_cursor?: RecordCursor;
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
