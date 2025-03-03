import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { type ModelMetadata, CommonPaths } from "$lib/scripts/types";
import { type AsyncResponseResolverReturnType } from "msw";
import { graphs } from "./graphs";
import {
  exampleFeatureDistribution,
  exampleAlerts,
  exampleUpdateAlert,
  exampleObservabilityMetrics,
  exampleAlertMetrics,
  sampleModelMetadata,
} from "./constants";

const handlers = [
  http.get(CommonPaths.AUTH_SETTINGS, async ({ request, params, cookies }) => {
    return HttpResponse.json({ opsml_auth: false });
  }),

  http.post("/opsml/cards/list", ({ request, params, cookies }) =>
    HttpResponse.json({
      cards: [
        {
          uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
        },
      ],
    })
  ),
  http.get("/opsml/cards/repositories", ({ request, params, cookies }) =>
    HttpResponse.json({
      repositories: ["model", "run", "data"],
    })
  ),
  http.get("/opsml/cards/registry/stats", ({ request, params, cookies }) =>
    HttpResponse.json({
      nbr_names: 1,
      nbr_versions: 1,
      nbr_repos: 1,
    })
  ),
  http.get("/opsml/cards/registry/query/page", ({ request, params, cookies }) =>
    HttpResponse.json({
      page: ["model", "repo", 10, 120, 110, 10],
    })
  ),

  http.get("/opsml/model/messages", ({ request, params, cookies }) =>
    HttpResponse.json([
      {
        message: "User this is a message",
        replies: [{ message: "User this is a reply" }],
      },
    ])
  ),

  http.put("/opsml/model/messages", ({ request, params, cookies }) =>
    HttpResponse.json([
      {
        message: "User this is a message",
        replies: [{ message: "User this is a reply" }],
      },
    ])
  ),

  http.patch("/opsml/model/messages", ({ request, params, cookies }) =>
    HttpResponse.json([
      {
        message: "User this is a message",
        replies: [{ message: "User this is a reply" }],
      },
    ])
  ),

  http.post("/opsml/data/card", ({ request, params, cookies }) =>
    HttpResponse.json({
      name: "test",
      repository: "test",
      version: "1.0.0",
      uid: "test",
      contact: "test",
      interface_type: "polars",
    })
  ),

  http.post("/opsml/run/card", ({ request, params, cookies }) =>
    HttpResponse.json({
      name: "test",
      repository: "test",
      version: "1.0.0",
      uid: "test",
      contact: "test",
    })
  ),

  http.post("/opsml/metrics", async ({ request }) => {
    const body = await request.json();

    // @ts-ignore
    if (body.names_only) {
      return HttpResponse.json({
        names: ["test"],
      });
    }

    return HttpResponse.json({
      metric: [
        {
          run_uid: "test",
          name: "test",
          value: 1,
          step: 1,
          timestamp: 1,
        },
        {
          run_uid: "test",
          name: "test",
          value: 2,
          step: 2,
          timestamp: 1,
        },
      ],
    });
  }),

  http.post("/opsml/parameters", async ({ request }) => {
    return HttpResponse.json({
      parameter: [
        {
          run_uid: "test",
          name: "test",
          value: 1,
          step: 1,
          timestamp: 1,
        },
      ],
    });
  }),

  http.get("/opsml/files/exists", async ({ request }) => {
    return HttpResponse.json({
      exists: true,
    });
  }),

  http.get("/opsml/files/view", async ({ request }) => {
    return HttpResponse.json({
      file_info: {
        name: "test",
        size: 10,
        type: "markdown",
        created: 234342,
        islink: false,
        mode: 10,
        uid: 10,
        gid: 10,
        mtime: 10,
        ino: 10,
        nlink: 10,
        uri: "uri",
        suffix: ".md",
      },
      content: {
        content: "test",
        view_type: "markdown",
      },
    });
  }),

  http.post(
    "/opsml/models/metadata",
    ({
      request,
      params,
      cookies,
    }): AsyncResponseResolverReturnType<ModelMetadata> =>
      HttpResponse.json(sampleModelMetadata)
  ),

  http.get("/opsml/files/list/info", async ({ request, params, cookies }) => {
    return HttpResponse.json({
      files: [
        {
          name: "test",
          size: 10,
          type: "markdown",
          created: 234342,
          islink: false,
          mode: 10,
          uid: 10,
          gid: 10,
          mtime: 10,
          ino: 10,
          nlink: 10,
          uri: "uri",
          suffix: ".md",
        },
      ],
      mtime: 10,
    });
  }),

  // get for /opsml/auth/user
  http.get("/opsml/auth/user", async ({ request, params, cookies }) => {
    return HttpResponse.json({
      user: {
        username: "test",
        is_active: true,
        scopes: {
          read: true,
          write: true,
          delete: true,
          admin: true,
        },
        watchlist: {
          model: ["test"],
          data: ["test"],
          run: ["test"],
        },
      },
    });
  }),

  // put for /opsml/auth/user
  http.put("/opsml/auth/user", async ({ request, params, cookies }) => {
    return HttpResponse.json({
      updated: true,
    });
  }),

  http.get("/opsml/auth/security", async ({ request, params, cookies }) => {
    const url = new URL(request.url);
    const username = url.searchParams.get("username")!;

    if (username === "active") {
      return HttpResponse.json({
        question: "test question",
        exists: true,
        error: "NA",
      });
    } else if (username === "inactive") {
      return HttpResponse.json({
        question: "NA",
        exists: false,
        error: "User not found",
      });
    }

    return HttpResponse.json({
      question: "NA",
      exists: false,
      error: "Error fetching security question",
    });
  }),

  http.get("/opsml/auth/user/exists", async ({ request, params, cookies }) => {
    const url = new URL(request.url);
    const username = url.searchParams.get("username")!;

    if (username === "active") {
      return HttpResponse.json({
        exists: true,
        username: "active",
      });
    }

    return HttpResponse.json({
      exists: false,
      username: "inactive",
    });
  }),

  http.post("/opsml/auth/temp", async ({ request, params, cookies }) => {
    const body = await request.json()!;

    // @ts-ignore
    let username = body.username!;

    if (username === "User not found") {
      return HttpResponse.json("User not found");
    }

    if (username === "Incorrect answer") {
      return HttpResponse.json("Incorrect answer");
    }

    if (username === "Error generating token") {
      return HttpResponse.json("Error generating token");
    }

    return HttpResponse.json("sadfusadf89s76df0safshd");
  }),

  http.post("/opsml/auth/register", async ({ request, params, cookies }) => {
    return new HttpResponse("Registered", {
      status: 200,
    });
  }),

  http.get("/opsml/metrics/hardware", async ({ request, params, cookies }) => {
    return HttpResponse.json({
      metrics: [
        {
          run_uid: "0a441b4ca2e444639182b72f0a52e17a",
          created_at: "2024-08-29T00:59:45.652409",
          metrics: {
            cpu: {
              cpu_percent_utilization: 27.61818181818182,
              cpu_percent_per_core: [
                45.1, 33.5, 25.6, 18.7, 15.1, 19.5, 31.4, 31.3, 28, 25.7, 29.9,
              ],
              compute_overall: 27.6,
              compute_utilized: 0.1,
              load_avg: 4.46142578125,
            },
            memory: {
              sys_ram_total: 19327352832,
              sys_ram_used: 13911949312,
              sys_ram_available: 5415403520,
              sys_ram_percent_used: 72,
              sys_swap_total: null,
              sys_swap_used: null,
              sys_swap_free: null,
              sys_swap_percent: null,
            },
            network: {
              bytes_recv: 106805089.39456193,
              bytes_sent: 205173711.53836402,
            },
            gpu: null,
          },
        },
        {
          run_uid: "0a441b4ca2e444639182b72f0a52e17a",
          created_at: "2024-08-29T01:05:45.652409",
          metrics: {
            cpu: {
              cpu_percent_utilization: 27.61818181818182,
              cpu_percent_per_core: [
                45.1, 33.5, 25.6, 18.7, 15.1, 19.5, 31.4, 31.3, 28, 25.7, 29.9,
              ],
              compute_overall: 27.6,
              compute_utilized: 0.1,
              load_avg: 4.46142578125,
            },
            memory: {
              sys_ram_total: 19327352832,
              sys_ram_used: 13911949312,
              sys_ram_available: 5415403520,
              sys_ram_percent_used: 72,
              sys_swap_total: null,
              sys_swap_used: null,
              sys_swap_free: null,
              sys_swap_percent: null,
            },
            network: {
              bytes_recv: 106805089.39456193,
              bytes_sent: 205173711.53836402,
            },
            gpu: null,
          },
        },
        {
          run_uid: "0a441b4ca2e444639182b72f0a52e17a",
          created_at: "2024-08-29T01:10:45.652409",
          metrics: {
            cpu: {
              cpu_percent_utilization: 27.61818181818182,
              cpu_percent_per_core: [
                45.1, 33.5, 25.6, 18.7, 15.1, 19.5, 31.4, 31.3, 28, 25.7, 29.9,
              ],
              compute_overall: 27.6,
              compute_utilized: 0.1,
              load_avg: 4.46142578125,
            },
            memory: {
              sys_ram_total: 19327352832,
              sys_ram_used: 13911949312,
              sys_ram_available: 5415403520,
              sys_ram_percent_used: 72,
              sys_swap_total: null,
              sys_swap_used: null,
              sys_swap_free: null,
              sys_swap_percent: null,
            },
            network: {
              bytes_recv: 106805089.39456193,
              bytes_sent: 205173711.53836402,
            },
            gpu: null,
          },
        },
      ],
    });
  }),

  http.get("/opsml/runs/graphs", async ({ request, params, cookies }) => {
    return HttpResponse.json(graphs);
  }),

  http.get(
    "/opsml/scouter/drift/profile",
    async ({ request, params, cookies }) => {
      return HttpResponse.json({
        profile: {
          features: {
            col1: {
              id: "col1",
              center: 0.0,
              one_ucl: 0.0,
              one_lcl: 0.0,
              two_ucl: 0.0,
              two_lcl: 0.0,
              three_ucl: 0.0,
              three_lcl: 0.0,
              timestamp: "2024-08-29T01:10:45.652409",
            },
          },
          config: {
            sample_size: 100,
            sample: true,
            name: "test",
            repository: "test",
            version: "1.0.0",
            feature_map: undefined,
            targets: [],
            alert_config: {
              dispatch_type: "Console",
              rule: {
                rule: "8 8 8 8 8 8 8 8",
                zones_to_monitor: ["Zone 1", "Zone 2", "Zone 3", "Zone 4"],
              },
              schedule: "0 0 0 0 0 0 0 0",
              dispatch_kwargs: {},
            },
          },
          scouter_version: "1.0.0",
        },
      });
    }
  ),

  http.put(CommonPaths.DRIFT_PROFILE, async ({ request, params, cookies }) => {
    return HttpResponse.json({
      complete: true,
      message: "Drift profile updated",
    });
  }),

  http.get(CommonPaths.DRIFT_VALUES, async ({ request, params, cookies }) => {
    const url = new URL(request.url);
    const feature = url.searchParams.get("feature")!;

    // check if feature is undefined
    if (feature) {
      if (feature === "col1") {
        return HttpResponse.json({
          features: {
            col_1: {
              created_at: [
                "2024-09-18T01:12:00",
                "2024-09-18T01:26:24",
                "2024-09-18T01:40:48",
                "2024-09-18T01:55:12",
                "2024-09-18T02:09:36",
              ],
              values: [
                1.0530614698813359, -0.03748357969929229, 0.1782311377309393,
                0.44125417583912063, -0.6577854789448841,
              ],
            },
          },
        });
      } else {
        return HttpResponse.json({
          features: {},
        });
      }
    } else {
      return HttpResponse.json({
        features: {
          all_features: {
            created_at: [
              "2024-09-18T01:12:00",
              "2024-09-18T01:26:24",
              "2024-09-18T01:40:48",
              "2024-09-18T01:55:12",
              "2024-09-18T02:09:36",
            ],
            values: [
              1.0530614698813359, -0.03748357969929229, 0.1782311377309393,
              0.44125417583912063, -0.6577854789448841,
            ],
          },
        },
      });
    }
  }),

  http.get(
    CommonPaths.FEATURE_DISTRIBUTION,
    async ({ request, params, cookies }) => {
      return HttpResponse.json(exampleFeatureDistribution);
    }
  ),

  http.get(CommonPaths.MONITOR_ALERTS, async ({ request, params, cookies }) => {
    return HttpResponse.json(exampleAlerts);
  }),
  http.put(CommonPaths.MONITOR_ALERTS, async ({ request, params, cookies }) => {
    return HttpResponse.json(exampleUpdateAlert);
  }),

  http.get(
    CommonPaths.MONITOR_ALERT_METRICS,
    async ({ request, params, cookies }) => {
      return HttpResponse.json(exampleAlertMetrics);
    }
  ),

  http.get(
    CommonPaths.OBSERVABILITY_METRICS,
    async ({ request, params, cookies }) => {
      return HttpResponse.json(exampleObservabilityMetrics);
    }
  ),
];

export const server = setupServer(...handlers);
