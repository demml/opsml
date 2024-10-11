import {
  type DriftProfileResponse,
  CommonPaths,
  type UpdateProfileResponse,
  type FeatureDriftValues,
  type SpcDriftProfile,
  type SpcFeatureDriftProfile,
  type DriftValues,
  type ChartjsData,
  type SpcFeatureDistribution,
  type TimestampData,
  type MonitorAlerts,
  TimeWindow,
  type UpdateAlert,
  type AlertMetrics,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";
import {
  type MonitoringVizData,
  type ObservabilityMetrics,
} from "$lib/scripts/monitoring/types";

export function generateTimestampsAndZeros(x: number): TimestampData {
  const now: Date = new Date();
  const pastTime: Date = new Date(now.getTime() - x * 60 * 1000);
  const interval: number = (now.getTime() - pastTime.getTime()) / 29; // 29 intervals for 30 timestamps

  const timestamps: string[] = [];
  for (let i = 0; i < 30; i++) {
    const timestamp: Date = new Date(pastTime.getTime() + i * interval);
    timestamps.push(timestamp.toISOString());
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const zeros: number[] = new Array(30).fill(0);

  return { timestamps, zeros };
}

export function createTimeWindowTimestamps(
  timeWindow: TimeWindow
): TimestampData {
  switch (timeWindow) {
    case TimeWindow.FiveMinutes:
      return generateTimestampsAndZeros(5);
    case TimeWindow.FifteenMinutes:
      return generateTimestampsAndZeros(15);
    case TimeWindow.ThirtyMinutes:
      return generateTimestampsAndZeros(30);
    case TimeWindow.OneHour:
      return generateTimestampsAndZeros(60);
    case TimeWindow.SixHours:
      return generateTimestampsAndZeros(360);
    case TimeWindow.TwelveHours:
      return generateTimestampsAndZeros(720);
    case TimeWindow.TwentyFourHours:
      return generateTimestampsAndZeros(1440);
    case TimeWindow.TwoDays:
      return generateTimestampsAndZeros(2880);
    case TimeWindow.FiveDays:
      return generateTimestampsAndZeros(7200);
  }

  return generateTimestampsAndZeros(5);
}

/// Get drift profile
/// @param name - name of the model
/// @param repository - repository of the model
/// @param version - version of the model
export async function getDriftProfile(
  repository: string,
  name: string,
  version: string
): Promise<DriftProfileResponse> {
  const profile_response = await apiHandler.get(
    `${CommonPaths.DRIFT_PROFILE}?${new URLSearchParams({
      repository: repository,
      name: name,
      version: version,
    }).toString()}`
  );

  const response = (await profile_response.json()) as DriftProfileResponse;
  return response;
}

/// Update drift profile
/// @param profile - drift profile
export async function updateDriftProfile(
  repository: string,
  version: string,
  name: string,
  profile: string
): Promise<UpdateProfileResponse> {
  const body = {
    name: name,
    repository: repository,
    version: version,
    profile: profile,
  };

  const update_response = await apiHandler.put(CommonPaths.DRIFT_PROFILE, body);

  const response = (await update_response.json()) as UpdateProfileResponse;
  return response;
}

/// get feature drift values
/// @param repository - repository of the model
/// @param name - name of the model
/// @param version - version of the model
/// @param time_window - time window for drift values
/// @param feature - optional feature to filter for drift values
export async function getFeatureDriftValues(
  repository: string,
  name: string,
  version: string,
  time_window: string,
  max_data_points: number,
  feature?: string
): Promise<FeatureDriftValues> {
  const params = {
    repository: repository,
    name: name,
    version: version,
    time_window: time_window,
    max_data_points: max_data_points.toString(),
  };

  if (feature) {
    params["feature"] = feature;
  }

  const values_response = await apiHandler.get(
    `${CommonPaths.DRIFT_VALUES}?${new URLSearchParams(params).toString()}`
  );

  const response = (await values_response.json()) as FeatureDriftValues;

  // check if feature is available
  if (Object.keys(response.features).length === 0) {
    const window = TimeWindow[time_window] as TimeWindow;
    const createdData = createTimeWindowTimestamps(window);
    response.features = {
      [feature!]: {
        created_at: createdData.timestamps,
        values: createdData.zeros,
      },
    };
  }

  return response;
}

// get feature distribution
/// @param repository - repository of the model
/// @param name - name of the model
/// @param version - version of the model
/// @param time_window - time window for values
/// @param feature - feature to filter for
export async function getSpcFeatureDistributionValues(
  repository: string,
  name: string,
  version: string,
  time_window: string,
  max_data_points: number,
  feature: string
): Promise<SpcFeatureDistribution> {
  const params = {
    repository: repository,
    name: name,
    version: version,
    time_window: time_window,
    max_data_points: max_data_points.toString(),
    feature: feature,
  };

  const values_response = await apiHandler.get(
    `${CommonPaths.FEATURE_DISTRIBUTION}?${new URLSearchParams(
      params
    ).toString()}`
  );

  const response = (await values_response.json()) as SpcFeatureDistribution;

  return response;
}

/// get feature boundaries
/// @param feature - name of the feature
/// @param profile - drift profile
export function getSpcFeatureProfile(
  feature: string,
  drift_profile: SpcDriftProfile
): SpcFeatureDriftProfile {
  return drift_profile.features[feature];
}

export const handleResize = (chart) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
  chart.resize();
};

export function createSpcDriftViz(
  driftValues: DriftValues,
  feature: SpcFeatureDriftProfile
): ChartjsData {
  const labels = driftValues.created_at.map((date) => new Date(date));
  const values = driftValues.values;
  const label = feature.id;
  const grace = "10%";
  const legend = {
    display: false,
  };

  const zoomOptions = {
    pan: {
      enabled: true,
      mode: "xy",
      modifierKey: "ctrl",
    },
    zoom: {
      mode: "xy",
      drag: {
        enabled: true,
        borderColor: "rgb(54, 162, 235)",
        borderWidth: 1,
        backgroundColor: "rgba(54, 162, 235, 0.3)",
      },
    },
  };

  const data = {
    labels: labels,
    datasets: [
      {
        label: label,
        data: values,
        borderColor: "rgba(0, 0, 0, 1)",
        backgroundColor: "rgba(0, 0, 0, 1)",
        pointRadius: 0,
        tension: 0.1,
      },
    ],
  };

  return {
    type: "line",
    data: data,
    options: {
      plugins: {
        zoom: zoomOptions,
        legend,
        annotation: {
          annotations: {
            UpperOneTwo: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.one_ucl,
              yMax: feature.two_ucl,
              backgroundColor: "rgba(75, 57, 120, 0.1)",
              borderWidth: 0,
            },
            LowerOneTwo: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.two_lcl,
              yMax: feature.one_lcl,
              backgroundColor: "rgba(75, 57, 120, 0.1)",
              borderWidth: 0,
            },
            UpperTwoThree: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.two_ucl,
              yMax: feature.three_ucl,
              backgroundColor: "rgba(75, 57, 120, 0.25)",
              borderWidth: 0,
            },
            LowerTwoThree: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.three_lcl,
              yMax: feature.two_lcl,
              backgroundColor: "rgba(75, 57, 120, 0.25)",
              borderWidth: 0,
            },
            UpperOutOfBounds: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.three_ucl,
              backgroundColor: "rgba(75, 57, 120, 0.50)",
              borderWidth: 0,
            },
            LowerOutOfBounds: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMax: feature.three_lcl,
              backgroundColor: "rgba(75, 57, 120, 0.50)",
              borderWidth: 0,
            },
            center: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.center,
              yMax: feature.center,
              borderColor: "rgba(4, 205, 155, 1)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "center",
                position: "end",
                backgroundColor: "rgba(4, 205, 155, 1)",
              },
            },
            zone1U: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.one_ucl,
              yMax: feature.one_ucl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 1",
                position: "end",
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
            zone1L: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.one_lcl,
              yMax: feature.one_lcl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 1",
                position: "end",
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
            zone2U: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.two_ucl,
              yMax: feature.two_ucl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 2",
                position: "end",
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
            zone2L: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.two_lcl,
              yMax: feature.two_lcl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 2",
                position: "end",
                fontSize: 2,
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
            zone3U: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.three_ucl,
              yMax: feature.three_ucl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 3",
                position: "end",
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
            zone3L: {
              type: "line",
              drawTime: "beforeDatasetsDraw",
              yMin: feature.three_lcl,
              yMax: feature.three_lcl,
              borderColor: "rgba(0, 0, 0, 0.25)",
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                display: true,
                content: "Zone 3",
                position: "end",
                backgroundColor: "rgba(75, 57, 120, 0.5)",
              },
            },
          },
        },
      },
      responsive: true,
      onresize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          type: "time",
          time: {
            displayFormats: {
              year: "YYYY",
              day: "DD-MM-YYYY",
              hour: "HH:mm",
              minute: "HH:mm",
              second: "HH:mm:ss",
            },
          },
          title: { display: true, text: "Time" },
          ticks: {
            maxTicksLimit: 30,
          },
        },
        y: {
          grace: grace,
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          title: { display: true, text: "Feature Values" },
          ticks: {
            maxTicksLimit: 30,
          },
        },
      },
      layout: {
        padding: 10,
      },
    },
  };
}

export function buildSpcFeatureDistributionViz(
  featureValues: SpcFeatureDistribution,
  feature: SpcFeatureDriftProfile
): ChartjsData {
  const refData = [
    { x: feature.three_lcl, y: 0.01 },
    { x: feature.two_lcl, y: 0.049 },
    { x: feature.one_lcl, y: 0.25 },
    { x: feature.center, y: 0.4 },
    { x: feature.one_ucl, y: 0.25 },
    { x: feature.two_ucl, y: 0.049 },
    { x: feature.three_ucl, y: 0.01 },
  ];

  const currData = [
    { x: featureValues.percentile_10, y: featureValues.val_10 },
    { x: featureValues.percentile_20, y: featureValues.val_20 },
    { x: featureValues.percentile_30, y: featureValues.val_30 },
    { x: featureValues.percentile_40, y: featureValues.val_40 },
    { x: featureValues.percentile_50, y: featureValues.val_50 },
    { x: featureValues.percentile_60, y: featureValues.val_60 },
    { x: featureValues.percentile_70, y: featureValues.val_70 },
    { x: featureValues.percentile_80, y: featureValues.val_80 },
    { x: featureValues.percentile_90, y: featureValues.val_90 },
    { x: featureValues.percentile_100, y: featureValues.val_100 },
  ];

  const refDataset = {
    type: "line",
    data: refData,
    borderColor: "rgba(4, 205, 155, 1)",
    backgroundColor: "rgba(4, 205, 155, 0.2)",
    borderWidth: 2,
    pointRadius: 0,
    tension: 0.4,
    fill: true,
    label: "Reference",
    order: 1,
  };

  const currDataset = {
    type: "line",
    data: currData,
    backgroundColor: "rgba(75, 57, 120, 0.5)",
    borderColor: "rgba(75, 57, 120, 1)",
    pointRadius: 0,
    borderWidth: 2,
    tension: 0.4,
    fill: true,
    label: "Current",
  };

  const data = {
    datasets: [currDataset, refDataset],
  };

  return {
    type: "bar",
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          type: "linear",
        },
        y: {
          grace: "10%",
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          ticks: {
            maxTicksLimit: 30,
          },
          beginAtZero: true,
        },
      },
    },
  };
}

export async function createSpcFeatureDistributionViz(
  repository: string,
  name: string,
  version: string,
  feature: string,
  time_window: string,
  max_data_points: number,
  feature_profile: SpcFeatureDriftProfile
): Promise<ChartjsData> {
  const featureValues = await getSpcFeatureDistributionValues(
    repository,
    name,
    version,
    time_window,
    max_data_points,
    feature
  );
  return buildSpcFeatureDistributionViz(featureValues, feature_profile);
}

export async function rebuildSpcDriftViz(
  repository: string,
  name: string,
  version: string,
  timeWindow: string,
  max_data_points: number,
  feature: string,
  featureProfile: SpcFeatureDriftProfile
): Promise<MonitoringVizData> {
  const featureValues = await getFeatureDriftValues(
    repository,
    name,
    version,
    timeWindow,
    max_data_points,
    feature
  );

  const featureDriftViz = createSpcDriftViz(
    featureValues.features[feature],
    featureProfile
  );

  const featureDistViz = await createSpcFeatureDistributionViz(
    repository,
    name,
    version,
    feature,
    timeWindow,
    max_data_points,
    featureProfile
  );

  const monitorVizData: MonitoringVizData = {
    driftVizData: featureDriftViz,
    featureDistVizData: featureDistViz,
  };

  return monitorVizData;
}

/// get alerts from scouter-server for a model
/// @param repository - repository of the model
/// @param name - name of the model
/// @param version - version of the model
/// @returns MonitorAlerts
export async function getMonitorAlerts(
  repository: string,
  name: string,
  version: string
): Promise<MonitorAlerts> {
  const profile_response = await apiHandler.get(
    `${CommonPaths.MONITOR_ALERTS}?${new URLSearchParams({
      repository: repository,
      name: name,
      version: version,
      active: "true",
      limit: "50",
    }).toString()}`
  );

  const response = (await profile_response.json()) as MonitorAlerts;
  return response;
}

export async function updateMonitorAlert(
  id: number,
  status: string
): Promise<UpdateAlert> {
  const body = {
    id: id,
    status: status,
  };

  const profile_response = await apiHandler.put(
    CommonPaths.MONITOR_ALERTS,
    body
  );

  const response = (await profile_response.json()) as UpdateAlert;
  return response;
}

/// get alerts metrics from scouter-server for a model
/// @param repository - repository of the model
/// @param name - name of the model
/// @param version - version of the model
/// @param time_window - time window for values
/// @param max_data_points - maximum number of data points
export async function getAlertMetrics(
  repository: string,
  name: string,
  version: string,
  time_window: string,
  max_data_points: number
): Promise<AlertMetrics> {
  const params = {
    repository: repository,
    name: name,
    version: version,
    time_window: time_window,
    max_data_points: max_data_points.toString(),
  };

  const values_response = await apiHandler.get(
    `${CommonPaths.MONITOR_ALERT_METRICS}?${new URLSearchParams(
      params
    ).toString()}`
  );

  const response = (await values_response.json()) as AlertMetrics;

  return response;
}

export function createAlertMetricViz(alertMetrics: AlertMetrics): ChartjsData {
  const labels = alertMetrics.created_at.map((date) => new Date(date));
  const active = alertMetrics.active;
  const acknowledged = alertMetrics.acknowledged;

  const grace = "10%";
  const legend = {
    display: false,
  };

  const data = {
    labels: labels,
    datasets: [
      {
        label: "Active",
        data: active,
        borderWidth: 1,
        borderColor: "rgba(245, 77, 85, 1)",
        backgroundColor: "rgba(245, 77, 85, 0.4)",
      },
      {
        label: "Acknowledged",
        data: acknowledged,
        borderWidth: 1,
        borderColor: "rgba(4, 205, 155, 1)",
        backgroundColor: "rgba(4, 205, 155, 0.4)",
      },
    ],
  };

  const zoomOptions = {
    pan: {
      enabled: true,
      mode: "xy",
      modifierKey: "ctrl",
    },
    zoom: {
      mode: "xy",
      drag: {
        enabled: true,
        borderColor: "rgb(54, 162, 235)",
        borderWidth: 1,
        backgroundColor: "rgba(54, 162, 235, 0.3)",
      },
    },
  };

  return {
    type: "bar",
    data: data,
    options: {
      plugins: {
        zoom: zoomOptions,
        legend,
        annotation: {},
      },
      responsive: true,
      onresize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          type: "time",
          time: {
            displayFormats: {
              year: "YYYY",
              day: "DD-MM-YYYY",
              hour: "HH:mm",
              minute: "HH:mm",
              second: "HH:mm:ss",
            },
          },
          title: { display: true, text: "Time" },
          ticks: {
            maxTicksLimit: 30,
          },
        },
        y: {
          stacked: true,
          grace: grace,
          border: {
            width: 2,
            color: "rgba(0, 0, 0, 1)",
          },
          grid: {
            display: false,
          },
          title: { display: true, text: "Alert Metrics" },
          ticks: {
            maxTicksLimit: 30,
          },
        },
      },
      layout: {
        padding: 10,
      },
    },
  };
}

export async function rebuildAlertMetricViz(
  repository: string,
  name: string,
  version: string,
  timeWindow: string,
  max_data_points: number
): Promise<ChartjsData> {
  const alertMetrics = await getAlertMetrics(
    repository,
    name,
    version,
    timeWindow,
    max_data_points
  );

  return createAlertMetricViz(alertMetrics);
}

export async function getObservabilityMetrics(
  repository: string,
  name: string,
  version: string,
  time_window: string,
  max_data_points: number
): Promise<ObservabilityMetrics> {
  const params = {
    repository: repository,
    name: name,
    version: version,
    time_window: time_window,
    max_data_points: max_data_points.toString(),
  };

  const values_response = await apiHandler.get(
    `${CommonPaths.OBSERVABILITY_METRICS}?${new URLSearchParams(
      params
    ).toString()}`
  );

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const response = (await values_response.json()) as ObservabilityMetrics;
  return response;
}
