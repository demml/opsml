import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const handlers = [
  http.post("/opsml/cards/list", ({ request, params, cookies }) => HttpResponse.json({
    cards: [
      {
        uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
      },
    ],
  })),
  http.get("/opsml/cards/repositories", ({ request, params, cookies }) => HttpResponse.json({
    repositories: ["model", "run", "data"],
  })),
  http.get("/opsml/cards/registry/stats", ({ request, params, cookies }) => HttpResponse.json({
    nbr_names: 1,
    nbr_versions: 1,
    nbr_repos: 1,
  })),
  http.get("/opsml/cards/registry/query/page", ({ request, params, cookies }) => HttpResponse.json({
    page: ["model", "repo", 10, 120, 110, 10],
  })),
];

export const server = setupServer(...handlers);
