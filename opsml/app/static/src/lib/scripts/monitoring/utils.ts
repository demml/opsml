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
  let label = "Feature drift for " + feature.id;
  let grace = "0%";

  let legend = {
    display: true,
    position: "bottom",
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
        pointRadius: 1,
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
              backgroundColor: "rgba(249, 179, 93, 0.25)",
              borderWidth: 0,
            },
            LowerOneTwo: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.two_lcl,
              yMax: feature.one_lcl,
              backgroundColor: "rgba(249, 179, 93, 0.25)",
              borderWidth: 0,
            },
            UpperTwoThree: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.two_ucl,
              yMax: feature.three_ucl,
              backgroundColor: "rgba(249, 179, 93, 0.50)",
              borderWidth: 0,
            },
            LowerTwoThree: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.three_lcl,
              yMax: feature.two_lcl,
              backgroundColor: "rgba(249, 179, 93, 0.50)",
              borderWidth: 0,
            },
            UpperOutOfBounds: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMin: feature.three_ucl,
              backgroundColor: "rgba(245, 77, 85, 0.50)",
              borderWidth: 0,
            },
            LowerOutOfBounds: {
              drawTime: "beforeDatasetsDraw",
              type: "box",
              yMax: feature.three_lcl,
              backgroundColor: "rgba(245, 77, 85, 0.50)",
              borderWidth: 0,
            },
          },
        },
      },
      responsive: true,
      onresize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: {
            displayFormats: {
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
          title: { display: true, text: "Feature Values" },
          ticks: {
            maxTicksLimit: 30,
          },
          grace,
        },
      },
      layout: {
        padding: 10,
      },
    },
  };
}
