import {
  type DriftProfileResponse,
  CommonPaths,
  type SuccessResponse,
  type FeatureDriftValues,
  type DriftProfile,
  type FeatureDriftProfile,
  type DriftValues,
  type ChartjsData,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";
import { draw } from "svelte/transition";

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
): Promise<SuccessResponse> {
  let body = {
    name: name,
    repository: repository,
    version: version,
    profile: profile,
  };

  const update_response = await apiHandler.put(CommonPaths.DRIFT_PROFILE, body);

  const response = (await update_response.json()) as SuccessResponse;
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
  let params = {
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

  return response;
}

/// get feature boundaries
/// @param feature - name of the feature
/// @param profile - drift profile
export function getFeatureProfile(
  feature: string,
  drift_profile: DriftProfile
): FeatureDriftProfile {
  return drift_profile.features[feature];
}

export const handleResize = (chart) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
  chart.resize();
};

export function createDriftViz(
  driftValues: DriftValues,
  feature: FeatureDriftProfile
): ChartjsData {
  let labels = driftValues.created_at.map((date) => new Date(date));
  let values = driftValues.values;
  let label = feature.id;
  let grace = "10%";
  let legend = {
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

  let data = {
    labels: labels,
    datasets: [
      {
        label: label,
        data: values,
        borderColor: "rgba(0, 0, 0, 1)",
        backgroundColor: "rgba(0, 0, 0, 1)",
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
