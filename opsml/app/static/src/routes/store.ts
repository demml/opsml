import { persisted } from "svelte-persisted-store";

export let empty: any = null;
export let emptyList: string[] = [];

export const AppStore = persisted("AppStore", {
  runStore: {
    homepage: {
      selectedRepo: empty,
      registryPage: empty,
      registryStats: empty,
    },
    cardPage: {
      compare: {
        Data: empty,
        SelectedMetrics: emptyList,
        MetricsToPlot: emptyList,
        CardsToCompare: emptyList,
        TableMetrics: empty,
        PlotSet: "bar",
        FilteredMetrics: emptyList,
        ShowTable: false,
      },
      metric: {
        Data: empty,
        SelectedMetrics: emptyList,
        MetricsToPlot: emptyList,
        TableMetrics: empty,
        PlotSet: "bar",
        FilteredMetrics: emptyList,
        ShowTable: false,
      },
    },
  },
});

export function resetStoreCardPage() {
  AppStore.update((store) => {
    // compare tab
    store.runStore.cardPage.compare.Data = empty;
    store.runStore.cardPage.compare.SelectedMetrics = emptyList;
    store.runStore.cardPage.compare.MetricsToPlot = emptyList;
    store.runStore.cardPage.compare.CardsToCompare = emptyList;
    store.runStore.cardPage.compare.TableMetrics = empty;
    store.runStore.cardPage.compare.PlotSet = "bar";
    store.runStore.cardPage.compare.FilteredMetrics = emptyList;
    store.runStore.cardPage.compare.ShowTable = false;

    // metric tab
    store.runStore.cardPage.metric.Data = empty;
    store.runStore.cardPage.metric.SelectedMetrics = emptyList;
    store.runStore.cardPage.metric.MetricsToPlot = emptyList;
    store.runStore.cardPage.metric.TableMetrics = empty;
    store.runStore.cardPage.metric.PlotSet = "bar";
    store.runStore.cardPage.metric.FilteredMetrics = emptyList;
    store.runStore.cardPage.metric.ShowTable = false;
    return store;
  });
}
