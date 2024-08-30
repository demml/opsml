import { persisted } from "svelte-persisted-store";
import type { an } from "vitest/dist/reporters-yx5ZTtEV.js";

let empty: any = null;
let emptyList: string[] = [];
export const runStore = persisted("preferences", {
  compareData: empty,
  compareSelectedMetrics: emptyList,
  compareMetricsToPlot: emptyList,
  compareCardsToCompare: emptyList,
  compareTableMetrics: empty,
  comparePlotSet: "bar",
  compareFilteredMetrics: emptyList,
  compareShowTable: false,
});
