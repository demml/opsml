/**
 * @vitest-environment jsdom
 */

import { expect, afterAll, afterEach, beforeAll, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import * as page from "../lib/scripts/homepage";
import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

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
