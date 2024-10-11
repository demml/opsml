import type {
  ChartjsData,
  ProfileType,
  SpcFeatureDriftProfile,
} from "$lib/scripts/types";

export interface MonitoringVizData {
  driftVizData: ChartjsData;
  featureDistVizData: ChartjsData;
}

export interface MonitorData {
  vizData: MonitoringVizData;
  feature: SpcFeatureDriftProfile;
}

export interface MonitoringLayoutPage {
  repository: string;
  name: string;
  version: string;
  feature: string | undefined;
  type: ProfileType;
  driftProfiles: Map<string, any>;
  showConfig: boolean;
  timeWindow: string;
  max_data_points: number;
}
