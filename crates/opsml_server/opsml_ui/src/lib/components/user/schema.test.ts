import { describe, expect, it } from "vitest";
import {
  validateLoginSchema,
  validatePasswordResetSchema,
  validateUserRegisterSchema,
} from "./schema";

describe("user schema validation", () => {
  it("validates login payloads", () => {
    expect(validateLoginSchema("user", "pw").success).toBe(true);
  });

  it("surfaces register password mismatch errors", () => {
    const result = validateUserRegisterSchema(
      "user@example.com",
      "Password1!",
      "Password2!",
      "user@example.com",
    );
    expect(result.success).toBe(false);
    expect(result.errors?.reEnterPassword).toContain("did not match");
  });

  it("falls back to username when email is missing", () => {
    const result = validateUserRegisterSchema(
      "user@example.com",
      "Password1!",
      "Password1!",
      "",
    );
    expect(result.success).toBe(true);
    expect(result.data?.email).toBe("user@example.com");
  });

  it("surfaces password reset confirm-password mismatch errors", () => {
    const result = validatePasswordResetSchema(
      "user",
      "recovery",
      "Password1!",
      "Password2!",
    );
    expect(result.success).toBe(false);
    expect(result.errors?.confirmPassword).toContain("did not match");
  });
});
