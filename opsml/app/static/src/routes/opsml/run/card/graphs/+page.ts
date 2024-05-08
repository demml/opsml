import { type Graph } from "$lib/scripts/types";
import { calculateTimeBetween, getRunGraphs } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string = url.searchParams.get("version")!;
  const graphs: Map<string, Graph> = await getRunGraphs(
    repository,
    name,
    version
  );

  console.log(graphs);

  return {
    graphs,
  };
}
