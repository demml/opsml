import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { type Files, type ModelMetadata } from "$lib/scripts/types";
import { type AsyncResponseResolverReturnType } from "msw";
import { user } from "./constants";

const handlers = [
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
      HttpResponse.json({
        model_name: "test",
        model_class: "test",
        model_type: "test",
        model_interface: "test",
        model_uri: "test",
        model_version: "test",
        model_repository: "test",
        opsml_version: "1.0.0",
        uid: "test",
        data_schema: {
          data_type: "test",
          input_features: "test",
          ouput_features: "test",
        },
      })
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
];

export const server = setupServer(...handlers);
