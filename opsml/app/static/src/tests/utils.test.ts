import { it, expect } from "vitest";
import * as page from "../lib/scripts/utils";

// test calculateTimeBetween
it("calculateTimeBetween", () => {
  const ts = new Date().getTime();
  const timeBetween = page.calculateTimeBetween(ts);
  expect(timeBetween).toMatch(/(^\d+ hours ago$)|(^\d+ days ago$)/);
});
