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
      compareData: empty,
      compareSelectedMetrics: emptyList,
      compareMetricsToPlot: emptyList,
      compareCardsToCompare: emptyList,
      compareTableMetrics: empty,
      comparePlotSet: "bar",
      compareFilteredMetrics: emptyList,
      compareShowTable: false,
    },
  },
});

export function resetStoreCardPage() {
  AppStore.update((store) => {
    store.runStore.cardPage.compareData = empty;
    store.runStore.cardPage.compareSelectedMetrics = emptyList;
    store.runStore.cardPage.compareMetricsToPlot = emptyList;
    store.runStore.cardPage.compareCardsToCompare = emptyList;
    store.runStore.cardPage.compareTableMetrics = empty;
    store.runStore.cardPage.comparePlotSet = "bar";
    store.runStore.cardPage.compareFilteredMetrics = emptyList;
    store.runStore.cardPage.compareShowTable = false;
    return store;
  });
}
