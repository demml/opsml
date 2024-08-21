import { it, expect } from "vitest";
import * as page from "../lib/scripts/utils";
import { type CardRequest, type Message } from "$lib/scripts/types";
import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
// test calculateTimeBetween
it("calculateTimeBetween", () => {
  const ts = new Date().getTime();
  const timeBetween = page.calculateTimeBetween(ts);
  expect(timeBetween).toMatch(/(^\d+ hours ago$)|(^\d+ days ago$)/);
});

it("cardRequest", async () => {
  const cardRequest: CardRequest = {
    registry_type: "run".toString(),
  };
  const cards = await page.listCards(cardRequest);
  expect(cards.cards).toEqual([
    {
      uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
    },
  ]);
});

it("getMessage", async () => {
  const message = await page.getMessages("uid", "model");
  expect(message).toEqual([
    {
      message: "User this is a message",
      replies: [{ message: "User this is a reply" }],
    },
  ]);
});

it("putMessage", async () => {
  const messageRequest: Message = {
    uid: "uid",
    registry: "model",
    content: "User this is a message",
    user: "user",
    votes: 0,
    parent_id: 0,
    created_at: 98709870,
  };
  await page.putMessage(messageRequest);
});

// patch messages
it("patchMessage", async () => {
  const messageRequest: Message = {
    uid: "uid",
    registry: "model",
    content: "User this is a message",
    user: "user",
    votes: 0,
    parent_id: 0,
    created_at: 98709870,
  };

  await page.patchMessage(messageRequest);
});

// get datacard
it("getDataCard", async () => {
  const cardRequest: CardRequest = {
    uid: "uid",
    registry_type: "data".toString(),
  };

  const dataCard = await page.getDataCard(cardRequest);
  expect(dataCard).toEqual({
    name: "test",
    repository: "test",
    version: "1.0.0",
    uid: "test",
    contact: "test",
    interface_type: "polars",
  });
});

// get runcard
it("getRunCard", async () => {
  const cardRequest: CardRequest = {
    uid: "uid",
    registry_type: "data".toString(),
  };

  const runCard = await page.getRunCard(cardRequest);
  expect(runCard).toEqual({
    name: "test",
    repository: "test",
    version: "1.0.0",
    uid: "test",
    contact: "test",
  });
});

// get run metric names
it("getRunMetricNames", async () => {
  const runCard = await page.getRunMetricNames("uid");
  expect(runCard).toEqual({
    names: ["test"],
  });
});

it("getRunMetrics", async () => {
  const runCard = await page.getRunMetrics("uid");
  expect(runCard).toEqual({
    test: [
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
});
