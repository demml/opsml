import { it, expect } from "vitest";
import { server } from "./server";
import { getSecurity, getToken, resetPassword } from "$lib/scripts/auth/utils";
import {
  registerUser,
  type RegisterResponse,
} from "$lib/scripts/auth/auth_routes";
import { type RegisterUser } from "$lib/scripts/types";

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

it("getToken", async () => {
  const noUserToken = await getToken("User not found", "test answer");
  expect(noUserToken.error).toEqual("User not found");
  expect(noUserToken.warnUser).toEqual(true);
  expect(noUserToken.token).toEqual("");

  const incorrectToken = await getToken("Incorrect answer", "test answer");
  expect(incorrectToken.error).toEqual("Incorrect answer");
  expect(incorrectToken.warnUser).toEqual(true);
  expect(incorrectToken.token).toEqual("");

  const errorToken = await getToken("Error generating token", "test answer");
  expect(errorToken.error).toEqual("Error generating token");
  expect(errorToken.warnUser).toEqual(true);
  expect(errorToken.token).toEqual("");

  const token = await getToken("user", "test answer");
  expect(token.error).toEqual("");
  expect(token.warnUser).toEqual(false);
  expect(token.token).toEqual("sadfusadf89s76df0safshd");
});

it("resetPassword", async () => {
  const noPower = await resetPassword(0, "test answer", "test password");
  expect(noPower.error).toEqual("Password is not strong enough");
  expect(noPower.warnUser).toEqual(true);

  const updated = await resetPassword(100, "user", "newPass");
  expect(updated.error).toEqual("");
  expect(updated.warnUser).toEqual(false);
});

it("registerUser", async () => {
  let user: RegisterUser = {
    username: "test",
    password: "test",
    email: "test",
    full_name: "test",
    security_question: "test",
    security_answer: "test",
  };

  let response = (await registerUser(user)) as RegisterResponse;
  expect(response.message).toEqual("User registered successfully");
});
