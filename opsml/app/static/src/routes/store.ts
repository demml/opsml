import { persisted } from "svelte-persisted-store";

export let empty: any = null;
export let emptyList: string[] = [];

export const RunPageStore = persisted("RunPageStore", {
  selectedRepo: empty,
  registryPage: empty,
  registryStats: empty,
});

export const ModelPageStore = persisted("ModelPageStore", {
  selectedRepo: empty,
  registryPage: empty,
  registryStats: empty,
});

export const DataPageStore = persisted("DataPageStore", {
  selectedRepo: empty,
  registryPage: empty,
  registryStats: empty,
});

export const RunCardStore = persisted("RunCardStore", {
  CompareMetricData: empty,
  CompareSelectedMetrics: emptyList,
  CompareMetricsToPlot: emptyList,
  CompareCardsToCompare: emptyList,
  CompareTableMetrics: empty,
  ComparePlotSet: "bar",
  CompareFilteredMetrics: emptyList,
  CompareShowTable: false,
});

export function resetRunCardStore() {
  RunCardStore.update((store) => {
    store.CompareMetricData = empty;
    store.CompareSelectedMetrics = emptyList;
    store.CompareMetricsToPlot = emptyList;
    store.CompareCardsToCompare = emptyList;
    store.CompareTableMetrics = empty;
    store.ComparePlotSet = "bar";
    store.CompareFilteredMetrics = emptyList;
    store.CompareShowTable = false;
    return store;
  });
}

//xport const AppStore = persisted("AppStore", {
// compareMetricData: empty,
// runStore: {
//   homepage: {
//     selectedRepo: empty,
//     registryPage: empty,
//     registryStats: empty,
//   },
//   cardPage: {
//     compare: {
//       MetricData: empty,
//       SelectedMetrics: emptyList,
//       MetricsToPlot: emptyList,
//       CardsToCompare: emptyList,
//       TableMetrics: empty,
//       PlotSet: "bar",
//       FilteredMetrics: emptyList,
//       ShowTable: false,
//     },
//     metric: {
//       MetricData: empty,
//       SelectedMetrics: emptyList,
//       MetricsToPlot: emptyList,
//       PlotSet: "bar",
//     },
//   },
// },
//);
//
//xport function resetStoreCardPage() {
// AppStore.update((store) => {
//   // compare tab
//
//   store.compareMetricData = empty;
//
//   if (store.runStore.cardPage.compare.SelectedMetrics) {
//     store.runStore.cardPage.compare.SelectedMetrics = emptyList;
//   }
//
//   if (store.runStore.cardPage.compare.MetricsToPlot) {
//     store.runStore.cardPage.compare.MetricsToPlot = emptyList;
//   }
//
//   if (store.runStore.cardPage.compare.CardsToCompare) {
//     store.runStore.cardPage.compare.CardsToCompare = emptyList;
//   }
//
//   if (store.runStore.cardPage.compare.TableMetrics) {
//     store.runStore.cardPage.compare.TableMetrics = empty;
//   }
//
//   store.runStore.cardPage.compare.PlotSet = "bar";
//
//   if (store.runStore.cardPage.compare.FilteredMetrics) {
//     store.runStore.cardPage.compare.FilteredMetrics = emptyList;
//   }
//   store.runStore.cardPage.compare.ShowTable = false;
//
//   // metric tab
//   store.runStore.cardPage.metric.MetricData = empty;
//   store.runStore.cardPage.metric.SelectedMetrics = emptyList;
//   store.runStore.cardPage.metric.MetricsToPlot = emptyList;
//   store.runStore.cardPage.metric.PlotSet = "bar";
//   return store;
// });
//
//
