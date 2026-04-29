import { describe, expect, it } from "vitest";
import {
  formatBytes,
  getFileTypeInfo,
  isAcceptableSuffix,
  timeAgo,
} from "./utils";

describe("files utils", () => {
  it("parses google-style timestamps in timeAgo", () => {
    expect(timeAgo("2025-07-09 15:26:44.373 +00:00:00")).toMatch(/ago$/);
  });

  it("formats bytes across units", () => {
    expect(formatBytes(999)).toBe("999.0 bytes");
    expect(formatBytes(1500)).toBe("1.5 kb");
  });

  it("classifies file types by mime type and suffix", () => {
    expect(getFileTypeInfo("png", "image/png")).toEqual({ type: "image" });
    expect(getFileTypeInfo("md", "text/plain")).toEqual({ type: "markdown" });
    expect(getFileTypeInfo("json", "application/json")).toEqual({
      type: "code",
      language: "json",
      requiresProcessing: true,
    });
    expect(getFileTypeInfo("txt", "text/plain")).toEqual({ type: "text" });
  });

  it("checks acceptable suffixes case-insensitively", () => {
    expect(isAcceptableSuffix("JSON")).toBe(true);
    expect(isAcceptableSuffix("exe")).toBe(false);
  });
});
