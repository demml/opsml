/**
 * @vitest-environment jsdom
 */

import {
  expect, test, afterAll, afterEach, beforeAll, it,
} from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import * as page from "./homepage";

const server = setupServer(
  // Describe network behavior with request handlers.
  // Tip: move the handlers into their own module and
  // import it across your browser and Node.js setups!
  http.post("/opsml/cards/list", ({ request, params, cookies }) => HttpResponse.json({
    cards: [
      {
        uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
      },
    ],
  })),
);

// Enable request interception.
beforeAll(() => server.listen());

// Don't forget to clean up afterwards.
afterAll(() => server.close());

// Reset handlers so that each test could alter them
// without affecting other, unrelated tests.
afterEach(() => server.resetHandlers());

it("get card test", async () => {
  const cards = await page.getCards("model");
  expect(cards).toEqual([
    {
      uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
    },
  ]);
});

it("recent card tests", async () => {
  const cards = await page.getRecentCards();
  expect(cards).toEqual({
    datacards: [
      {
        uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
      },
    ],
    modelcards: [
      {
        uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
      },
    ],
    runcards: [
      {
        uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
      },
    ],
  });
});
