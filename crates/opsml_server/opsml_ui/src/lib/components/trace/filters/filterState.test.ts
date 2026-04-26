import { describe, expect, it } from "vitest";
import { applyClientDurationFilter } from "./filterState.svelte";

type Row = {
  id: string;
  duration_ms: number | null;
};

const rows: Row[] = [
  { id: "null", duration_ms: null },
  { id: "50", duration_ms: 50 },
  { id: "100", duration_ms: 100 },
  { id: "200", duration_ms: 200 },
  { id: "300", duration_ms: 300 },
  { id: "400", duration_ms: 400 },
];

describe("applyClientDurationFilter", () => {
  it("returns original rows when no duration bounds are set", () => {
    const filtered = applyClientDurationFilter(rows, {});
    expect(filtered).toBe(rows);
  });

  it("applies both min and max bounds and excludes null durations", () => {
    const filtered = applyClientDurationFilter(rows, {
      duration_min_ms: 100,
      duration_max_ms: 300,
    });
    expect(filtered.map((row) => row.id)).toEqual(["100", "200", "300"]);
  });

  it("applies only max bound", () => {
    const filtered = applyClientDurationFilter(rows, {
      duration_max_ms: 100,
    });
    expect(filtered.map((row) => row.id)).toEqual(["50", "100"]);
  });
});
