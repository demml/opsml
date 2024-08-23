import { it, expect } from "vitest";
import * as page from "../lib/scripts/utils";
import {
  type CardRequest,
  type Message,
  type UpdateUserRequest,
  type ChartjsData,
} from "$lib/scripts/types";
import { server } from "./server";
import { getSecurity } from "$lib/scripts/auth/utils";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("getSecurity", async () => {
  const security = await getSecurity("active");
  expect(security.error).toEqual("");
  expect(security.warnUser).toEqual(false);
  expect(security.question).toEqual("test question");

  const nosecurity = await getSecurity("inactive");
  expect(nosecurity.error).toEqual("User does not exist");
  expect(nosecurity.warnUser).toEqual(true);

  const misssecurity = await getSecurity(undefined);
  expect(misssecurity.error).toEqual("Username cannot be empty");
  expect(misssecurity.warnUser).toEqual(true);
});
