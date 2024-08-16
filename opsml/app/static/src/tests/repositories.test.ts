import {
  expect, afterAll, afterEach, beforeAll, it,
} from "vitest";
import * as page from "../lib/scripts/repositories";
import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// test getRepos
it("getRepos", async () => {
  const repos = await page.getRepos("model");
  expect(repos).toEqual(["model", "run", "data"]);
});
