import { describe, expect, it, vi, beforeEach } from "vitest";
import { refreshAgentMonitoringData } from "./utils";
import { getMockAgentMonitoringPageData } from "$lib/components/scouter/evaluation/mockData";
import { RegistryType } from "$lib/utils";
import type { TimeRange } from "$lib/components/trace/types";
import type { DateTime } from "$lib/types";

const baseRange: TimeRange = {
  label: "Past 15 minutes",
  value: "15min",
  startTime: "2026-04-27T00:00:00.000Z" as DateTime,
  endTime: "2026-04-27T00:15:00.000Z" as DateTime,
  bucketInterval: "30 seconds",
};

const newRange: TimeRange = {
  label: "Past 1 Hour",
  value: "1hour",
  startTime: "2026-04-27T00:00:00.000Z" as DateTime,
  endTime: "2026-04-27T01:00:00.000Z" as DateTime,
  bucketInterval: "1 minute",
};

describe("getMockAgentMonitoringPageData", () => {
  it("always returns success status with mockMode: true", () => {
    const data = getMockAgentMonitoringPageData("uid-1", RegistryType.Prompt, baseRange);
    expect(data.status).toBe("success");
    expect(data.mockMode).toBe(true);
  });

  it("sets selectedTimeRange from the provided range", () => {
    const data = getMockAgentMonitoringPageData("uid-1", RegistryType.Prompt, newRange);
    expect(data.selectedTimeRange.startTime).toBe(newRange.startTime);
    expect(data.selectedTimeRange.endTime).toBe(newRange.endTime);
  });
});

describe("refreshAgentMonitoringData — mock mode", () => {
  it("regenerates selectedData from mock without calling fetch", async () => {
    const fetchSpy = vi.fn();
    const monitoringData = getMockAgentMonitoringPageData(
      "uid-2",
      RegistryType.Prompt,
      baseRange,
    );
    monitoringData.selectedTimeRange = newRange;

    await refreshAgentMonitoringData(fetchSpy as any, monitoringData);

    expect(fetchSpy).not.toHaveBeenCalled();
    expect(monitoringData.selectedData).toBeDefined();
  });

  it("updates selectedData when time range changes in mock mode", async () => {
    const monitoringData = getMockAgentMonitoringPageData(
      "uid-3",
      RegistryType.Prompt,
      baseRange,
    );
    const originalData = monitoringData.selectedData;
    monitoringData.selectedTimeRange = newRange;

    await refreshAgentMonitoringData(vi.fn() as any, monitoringData);

    // selectedData must be replaced (not the same object reference)
    expect(monitoringData.selectedData).not.toBe(originalData);
  });
});
