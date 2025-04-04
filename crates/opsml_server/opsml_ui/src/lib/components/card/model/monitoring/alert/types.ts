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
  feature: string;
  alert: Record<string, string>;
  id: number;
  status: string;
}
export interface AlertResponse {
  status: string;
  data: Alert[];
}
