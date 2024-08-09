import {
  expect, afterAll, afterEach, beforeAll, it,
} from "vitest";
import * as page from "../lib/scripts/registry_page";

import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// test getRegistryPage
it("getRegistryPage", async () => {
  const pageData = await page.getRegistryPage(
    "model",
    undefined,
    "repo",
    "model",
    0,
  );
  expect(pageData.page).toEqual(["model", "repo", 10, 120, 110, 10]);
});
