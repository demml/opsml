import { describe, expect, it } from "vitest";
import {
  A2AOperation,
  A2AOperationResolver,
  getHttpJsonPath,
  getOperationName,
} from "./a2aOperations";

describe("a2aOperations", () => {
  it("maps v0.3 JSON-RPC operations to slash-based names", () => {
    expect(getOperationName(A2AOperation.SendMessage, "0.3.0", "jsonrpc")).toBe(
      "message/send",
    );
  });

  it("maps v1 HTTP+JSON operations to colon paths without /v1 prefix", () => {
    expect(getHttpJsonPath(A2AOperation.SendMessage, "1.0")).toBe("/message:send");
  });

  it("normalizes bindings and versions in the resolver", () => {
    const resolver = new A2AOperationResolver("0.3.1", "REST");
    expect(resolver.isV0_3()).toBe(true);
    expect(resolver.getMethodName(A2AOperation.GetTask)).toBe("tasks/get");
    expect(resolver.getHttpJsonPath(A2AOperation.GetTask)).toBe("/v1/tasks");
  });
});
