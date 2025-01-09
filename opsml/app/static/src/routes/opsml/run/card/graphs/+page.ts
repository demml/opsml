import { type RunGraph } from "$lib/scripts/types";
import { getRunGraphs } from "$lib/scripts/utils";
import { RunCardStore } from "$routes/store";
import { get } from "svelte/store";

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;

  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  if (!get(RunCardStore).Graphs) {
    const graphs: Map<string, RunGraph> = await getRunGraphs(
      repository!,
      name!,
      version!
    );

    RunCardStore.update((store) => {
      store.Graphs = graphs;
      return store;
    });
  }
}
